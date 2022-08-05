# VeighNa框架的SQLite数据库接口

<p align="center">
  <img src ="https://vnpy.oss-cn-shanghai.aliyuncs.com/vnpy-logo.png"/>
</p>

<p align="center">
    <img src ="https://img.shields.io/badge/version-1.0.1-blueviolet.svg"/>
    <img src ="https://img.shields.io/badge/platform-windows|linux|macos-yellow.svg"/>
    <img src ="https://img.shields.io/badge/python-3.7|3.8|3.9|3.10-blue.svg" />
</p>

## 说明

基于peewee开发的SQLite数据库接口，无需另外安装配置数据库软件，易于使用适合初学者用户。

## 使用

在VeighNa中使用SQLite时，需要在全局配置中填写以下字段信息：

|名称|含义|必填|举例|
|---------|----|---|---|
|database.name|名称|是|sqlite|
|database.database|实例|是|database.db|
