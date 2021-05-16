import smtplib
import ssl
import json
import websockets
from datetime import datetime
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from django.contrib.auth import get_user_model
from celery import shared_task, Task, task

from LibrSite.celery import app  # app is your celery application
from . import models as olm

ws_path = "ws://127.0.0.1:8000/tasks/"      # should be dynamic


class CallbackTask(Task):
    def run(self, *args, **kwargs):
        pass

    def on_success(self, retval, task_id, args, kwargs):
        print("TaskID= %s, Result is %s" % (task_id, retval))

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        pass


@shared_task(name="update_book_rating", ignore_result=True, base=CallbackTask)
def update_book_rating(b_id):       # singular book update, in case of distributed tasks, not used
    try:
        book = olm.Book.objects.get(id=b_id)
        reviews = book.reviews.all()
        res = 0
        for r in reviews:
            res += r.rating
        if res != 0:
            res = res / len(reviews)
        book.rating = res
        book.save()
    except olm.Book.DoesNotExist:
        print("Book with passed id does not exist in DB")
        raise
    except Exception as exc:
        raise


class CommonNotifyingTask(Task):
    name = "stub"
    ignore_result = True    # no result needed

    def run(self, *args, **kwargs):
        pass

    def on_success(self, retval, task_id, args, kwargs):
        print("SUCCESS - Task = %s; TaskID = %s" % (self.name, task_id))

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        # async_to_sync(self.ws_send)({}, task_id, args, kwargs, note="FAILED")
        print("FAIL - Task = %s; TaskID = %s" % (self.name, task_id))

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        print("Got exception %s, retrying" % exc)

    async def ws_send(self, retval, task_id, args, kwargs, note=None):
        pack = {'type': 'task_message',
                'task': self.name,
                'task_id': task_id,
                'finished': datetime.now().strftime("%H:%M:%S %m/%d/%Y")}    # isoformat(microsecond=0)}
        if retval:                      # minimize pack size
            pack['result'] = retval
        if note:
            pack['note'] = note
        if args:
            pack['args'] = [args]
        if kwargs:
            pack['args'].append(kwargs)
        try:
            async with websockets.connect(ws_path) as websocket:
                await websocket.send(json.dumps(pack))
        except ConnectionRefusedError:
            print("Unable to report: Can't connect to ws")
            pass
        except Exception as exc:
            raise


class UpdateRatingsTask(CommonNotifyingTask):
    name = "update_ratings"

    length = 0

    def run(self, *args, **kwargs):
        try:
            all_books = olm.Book.objects.all()      # (id=b_id)
            all_reviews = olm.Review.objects.all()
            all_statuses = olm.ReadStatus.objects.all()
            for book in all_books:
                # update_book_rating.delay(book.id)     # in case of distributed tasks
                res = 0
                book.read_counter = len(all_statuses.filter(book=book))
                reviews = all_reviews.filter(book=book)
                if reviews:
                    for r in reviews:
                        res += r.rating
                    book.rating = res / len(reviews)
                else:
                    book.rating = 0
                book.save()
            self.length = len(all_books)
        except Exception as exc:
            raise
            # self.retry(countdown=10, exc=exc)

    def on_success(self, retval, task_id, args, kwargs):
        async_to_sync(self.ws_send)(retval, task_id, args, kwargs, note=self.length)
        super().on_success(retval, task_id, args, kwargs)
        # print("TaskID = %s, %d book ratings updated successfully" % task_id, self.len)


class SendMailTask(CommonNotifyingTask):
    name = "send_mail"

    def run(self, *args, **kwargs):
        try:
            with open("online_libr/pass.json") as file:     # file with sender's email and password
                cred = json.load(file)                      # should be passed, but I don't want to make encryption
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                server.login(cred["login"], cred["pass"])
                staff_list = get_user_model().objects.filter(is_staff=True)
                for person in staff_list:
                    server.sendmail(cred["login"], person.email, "Subject: Test\n\n %s" % args[0])
        except FileNotFoundError:
            print("No credentials file provided")
            raise   # No need to retry
        except get_user_model().DoesNotExist:
            print("No staff to send to")
            pass
        except Exception as exc:
            self.retry(countdown=10, exc=exc)
            raise

    def on_success(self, retval, task_id, args, kwargs):
        async_to_sync(self.ws_send)(retval, task_id, args, kwargs)
        super().on_success(retval, task_id, args, kwargs)
        # print("TaskID = %s, email sent succesfully" % task_id)


app.tasks.register(UpdateRatingsTask())
app.tasks.register(SendMailTask())  # no autodiscover :(
