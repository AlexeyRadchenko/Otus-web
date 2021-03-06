WEB-приложение: прием показаний приборов учета коммунальных услуг
===========
- Python - 3.6.3
- Django - 1.11.7
- Celery - 4.1.0
- Redis - 3.0.6
- Django Rest FrameWork - 3.7.6

Описание проекта:
------
[Ссылка на ТЗ!](https://gist.github.com/AlexeyRadchenko/6987015e4165f15fcaff9f797b805ad4)


Задачи:
------
- [ ] Обмен данными с внешней системой учета
    - [x] Загрузка/выгрузка Excel 97-2003 (xls)
    - [ ] Загрузка/выгрузка Excel 2007-2013 (xlsx)
    - [ ] Загрузка/выгрузка XML
- [x] Рендер шаблонов на стороне сервера
    - [x] пользователя
    - [x] диспетчера
    - [x] сотрудника РКЦ   
- [ ] Шаблоны
    - [x] Интерфейс пользователя
    - [ ] Интерфейс диспетчера
    - [ ] Интерфейс сотрудника РКЦ
- [ ] API
    - [x] Передача состояния процесса загрузки данных
    - [x] Запись дааных полученных от пользователей
    - [x] Получения данных для пользователя/сотрудников
    - [ ] Новая функция
    
Модель данных:
--------------
\*Не окончательный вариант!\*

![Текущая схема.][myimage]

[myimage]: http://bers-trg.fvds.ru/base.png

Интерфейс пользователя:
----------------------
![Интерфейс пользователя.][user_interface]

[user_interface]: http://bers-trg.fvds.ru/user_interface.png