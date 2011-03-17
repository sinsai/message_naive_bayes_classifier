#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlalchemy
from sqlalchemy.orm import scoped_session, sessionmaker, mapper
from sqlalchemy import MetaData
from sqlalchemy import Column, MetaData, Table, types
from datetime import datetime

class Message(object):
    pass

metadata = sqlalchemy.MetaData()

message = Table("message", metadata,
                Column('id', types.BigInteger(20), primary_key=True),
                Column('parent_id', types.BigInteger(20)),
                Column('incident_id', types.Integer(11)),
                Column('user_id', types.Integer(11)),
                Column('reporter_id', types.BigInteger(20)),
                Column('service_messageid', types.Unicode(100)),
                Column('message_from', types.Unicode(100)),
                Column('message_to', types.Unicode(100)),
                Column('message', types.Unicode),
                Column('message_detail', types.Unicode),
                Column('message_type', types.SmallInteger(4)),
                Column('message_date', types.DateTime),
                Column('message_level',types.SmallInteger(4)),
                mysql_engine = 'InnoDB',
                mysql_charset = 'utf8'
            )


def startSession(conf):
    
    config = {"sqlalchemy.url":
            "mysql://"+conf["dbuser"]+":"+conf["dbpass"]+"@"+conf["dbhost"]+"/"+conf["db"]+"?charset=utf8",
            "sqlalchemy.echo":"False"}
    engine = sqlalchemy.engine_from_config(config)
    
    dbSession = scoped_session(
                    sessionmaker(
                        autoflush = True,
                        autocommit = False,
                        bind = engine
                    )
                )

    mapper(Message, message)
    return dbSession
