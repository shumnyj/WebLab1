# WebLab2
Web Apps development lab #2 <br/>
Виконав: Троян Борис КВ-02мп <br/>
Звіт: https://docs.google.com/document/d/1Nekq2cubDDf5lmtroLPM2EhMUykoLmCgogW8b0g2wHI/edit?usp=sharing <br/>
 
Загальне завдання: розробити функції обміну даними між користувачами Web-додатка, а також адміністрування користувачами у реальному часі.<br/>
Інструменти розробки: Python 3, Django, Django Channels, redis, Pycharm Community Edition <br/>

Web-додаток має реалізовувати наступні функції: <br/>
- реєстрація користувача (поля: ім’я, email, стать, дата народження)  
- вхід до сайту (поля: email, пароль)  
- профіль користувача (поля у табличному вигляді)  
- про додаток (емблема додатку, короткий опис додатка)  
- робочі функції додатка (розробляється самостійно студентом відповідно до обраної тематики)  

На основі обраної тематики і реалізованого у лабораторній роботі №1 Web-додатку виконати розробку наступних функціональних вимог:<br/>
- Можливість передавати робочі дані додатку між користувачами у реальному часі. Наприклад, для калькулятора - передавати дані для обчислення, для будильника - дату і час спрацювання тощо.
- Адміністратору додатка мати можливість переглядати список користувачів, які працюють з додатком у даний час (список користувачів “онлайн”).
