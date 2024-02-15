create table users(email varchar(100), password varchar(100), firstname varchar(100), 
                   familyname varchar(100), gender varchar(100), city varchar(100), 
                   country varchar(100), primary key(email));

create table loggedInUsers(token varchar(100), email varchar(100), primary key(email));

create table messages(writer varchar(100), receiver varchar(100), content varchar(100),
                      foreign key(writer) references users(email), 
                      foreign key(receiver) references users(email));