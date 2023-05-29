## 简单通讯录

### 1. 依赖库
* os
* json
* typing

### 2. 结构
* main.py
* data.json

### 3. 功能

1. 查看通讯录
2. 添加联系人
3. 删除联系人
4. 修改联系人
5. 查询联系人
6. 退出程序

### 4. 实现

1. Data 和 DataFactory类管理数据，负责输入输出和格式化等
2. BaseMenu 作为基础菜单，接收DataFactory对象作为参数
3. MainMenu、DataMenu、AddMenu...继承BaseMenu，实现各自的功能
4. MainMenu作为主要菜单，循环调用各个菜单