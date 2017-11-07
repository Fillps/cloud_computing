drop table if exists plans;
create table plans (
  id integer primary key autoincrement,
  title text not null,
  price real not null,
  description text not null
);
