create table users(email varchar(50), password varchar(50), firstname varchar(50), 
                   familyname varchar(50), gender varchar(50), city varchar(50), 
                   country varchar(50), primary key(email));

create table loggedInUsers(token varchar(50), email varchar(50), primary key(email));