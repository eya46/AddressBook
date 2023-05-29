import os
from typing import List, Union, Type, Optional
import json


class Data:
    def __init__(self, num: Union[int, str], name: str, phone: Union[int, str], address: str):
        self.num = num
        self.name = self.parse_name(name)
        self.phone = self.parse_phone(phone)
        self.address = self.parse_address(address)

    def update(self, key: str, value):
        if hasattr(self, key):
            if key == "num":
                raise AttributeError(f"不能修改 {key}")
            elif key == "phone":
                if not isinstance(value, int):
                    raise TypeError(f"{key} 必须为 int")
            setattr(self, key, value)
        else:
            raise AttributeError(f"不存在该 {key}")

    def dict(self):
        return self.__dict__

    def fix(self):
        return str(self)

    def __str__(self):
        return f"{self.name}-{self.phone}-{self.address}"

    @staticmethod
    def parse_address(address: str):
        address = str(address).strip()
        if len(address) > 20 or len(address) < 4:
            raise ValueError("通讯地址 长度必须在 4-20 之间")
        return address

    @staticmethod
    def parse_name(name: str):
        name = str(name).strip()
        if len(name) > 10 or len(name) < 2:
            raise ValueError("姓名 长度必须在 2-10 之间")
        return name

    @staticmethod
    def parse_phone(phone: Union[str, int]):
        phone = str(phone).strip()
        if not phone.isdigit():
            raise TypeError("手机号 必须为 数字")
        if len(phone) != 11:
            raise ValueError("手机号 长度必须为 11")
        return int(phone)

    def save(self) -> str:
        return json.dumps(self.__dict__, ensure_ascii=False, indent=4)

    @staticmethod
    def read(data: Union[str, dict]) -> "Data":
        return Data(**(json.loads(data) if isinstance(data, str) else data))


class DataFactory:
    def __init__(self, path: str):
        self.path = path
        self.data = self.load_data(path)

    @staticmethod
    def load_data(path: str) -> List[Data]:
        if not path.endswith(".json"):
            raise TypeError("数据必须是json格式")
        if not os.path.exists(path):
            data = []
        else:
            with open(path, "r", encoding="utf-8") as f:
                data = json.loads(f.read())
        if not isinstance(data, list):
            raise TypeError("data must be list")
        return [Data.read(i) for i in data]

    def create(self, name: str, phone: Union[int, str], address: str):
        num = max([i.num for i in self.data] or [0]) + 1
        data = Data(num, name, phone, address)
        self.data.append(data)
        self.save_data()
        return data

    def save_data(self):
        with open(self.path, "w", encoding="utf-8") as f:
            f.write(json.dumps([i.dict() for i in self.data], ensure_ascii=False, indent=4))

    def search(self, data: str) -> Optional[Union[Data, List[Data]]]:
        res = []
        if data.isdigit():
            if len(data) == 11:
                res = [i for i in self.data if i.phone == int(data)]
            else:
                res = [i for i in self.data if i.num == int(data)]
        res.extend([i for i in self.data if data in i.fix()])

        if len(res) == 1:
            return res[0]
        elif len(res) > 1:
            return list(set(res))
        else:
            return None

    @staticmethod
    def type_data(data: List[Data]) -> str:
        data.sort(key=lambda x: x.num)
        # 格式化左对齐，保留 x个 字符位置
        res = [f"{'序号':<4}\t{'姓名':<8}\t{'手机号':<13}\t{'通讯地址':<20}"]
        for i in data:
            res.append(f"{i.num:<4}\t{i.name:<8}\t{i.phone:<13}\t{i.address:<20}")
        return "\n".join(res)


class BaseMenu:
    id: int
    name: str

    @classmethod
    def show_menu(cls):
        cls.print(f"{cls.id}. {cls.name}")

    def __init__(self, factory: DataFactory):
        self.factory = factory

    @staticmethod
    def print(*args, **kwargs):
        print(*args, **kwargs)

    @staticmethod
    def clear():
        # 想实现清屏，但不好搞
        ...

    @staticmethod
    def get_input(the_type: Type, show_msg: str = "请输入选项:"):
        choose = input(show_msg)

        try:
            return the_type(choose)
        except:
            BaseMenu.print("输入错误！")
            return None

    def action(self):
        ...

    def run(self):
        self.clear()
        self.action()
        self.print("\n")
        self.clear()


class MainMenu(BaseMenu):
    id = 0
    name = "主菜单"

    def action(self):
        while True:
            self.print("欢迎使用通讯录")
            DataMenu.show_menu()
            AddMenu.show_menu()
            DeleteMenu.show_menu()
            UpdateMenu.show_menu()
            QueryMenu.show_menu()
            ExitMenu.show_menu()

            choose = self.get_input(int, "请输入选项: ")
            if choose is None:
                continue

            menus = [DataMenu, AddMenu, DeleteMenu, UpdateMenu, QueryMenu, ExitMenu]
            for menu in menus:
                if menu.id == choose:
                    menu(self.factory).run()
                    break


class DataMenu(BaseMenu):
    id = 1
    name = "查看通讯录"

    def action(self):
        if len(self.factory.data) == 0:
            self.print("通讯录为空")
        else:
            self.print(self.factory.type_data(self.factory.data))


class AddMenu(BaseMenu):
    id = 2
    name = "添加联系人"

    def action(self):
        while True:
            try:
                name = Data.parse_name(input("请输入姓名: "))
                break
            except Exception as e:
                self.print(f"检查错误:{e}")

        while True:
            try:
                phone = Data.parse_phone(input("请输入手机号: "))
                break
            except Exception as e:
                self.print(f"检查错误:{e}")

        while True:
            try:
                address = Data.parse_address(input("请输入通讯地址: "))
                break
            except Exception as e:
                self.print(f"检查错误:{e}")

        try:
            data = self.factory.create(name, phone, address)
        except Exception as e:
            self.print(f"添加失败:{e}")
        else:
            self.print(f"添加成功！{data}")


class DeleteMenu(BaseMenu):
    id = 3
    name = "删除联系人"

    def action(self):
        data = self.get_input(str, "请输入编号/姓名/手机号: ")
        if len(data) == 0:
            self.print("返回主菜单！")
            return
        datas = self.factory.search(data)
        if datas is None:
            self.print("未找到联系人！")
        elif isinstance(datas, Data):
            self.print(f"已找到联系人：{datas}")
            choose: str = self.get_input(str, "是否删除？(y/n): ")
            if choose.lower() == "y":
                self.factory.data.remove(datas)
                self.factory.save_data()
                self.print(f"删除成功！{datas}")
            else:
                self.print("取消删除！")
        else:
            self.print(f"已找到联系人：\n{self.factory.type_data(datas)}")
            num = self.get_input(int, "请选择要删除的编号: ")
            if num is None:
                self.print("取消删除！")
            else:
                for i in datas:
                    if i.num == num:
                        choose: str = self.get_input(str, "是否删除？(y/n): ")
                        if choose.lower() == "y":
                            self.factory.data.remove(i)
                            self.factory.save_data()
                            self.print(f"删除成功！{i}")
                        else:
                            self.print("取消删除！")
                        break
                else:
                    self.print("未找到联系人！")


class UpdateMenu(BaseMenu):
    id = 4
    name = "修改联系人"

    def action(self):
        data = self.get_input(str, "请输入编号/姓名/手机号: ")
        if len(data) == 0:
            self.print("返回主菜单！")
            return
        datas = self.factory.search(data)
        if datas is None:
            self.print("未找到联系人！")
        elif isinstance(datas, Data):
            self.print(f"已找到联系人：{datas}")
            self.update_data(datas)
        else:
            self.print(f"已找到联系人：\n{self.factory.type_data(datas)}")
            choose: int = self.get_input(int, "请输入要修改的编号: ")
            if choose is None:
                self.print("取消修改！")
            for i in datas:
                if i.num == choose:
                    self.print(f"选中的联系人：{i}")
                    self.update_data(i)
                    break
            else:
                self.print("未找到联系人！")

    def update_data(self, data: Data):
        raw_data = str(data)
        while True:
            try:
                name = self.get_input(str, "请输入姓名(空格不修改): ")
                name = None if name is None or name.strip() == "" else Data.parse_name(name)
                break
            except Exception as e:
                self.print(f"姓名输入错误:{e}")
        while True:
            try:
                phone = self.get_input(str, "请输入手机号(空格不修改): ")
                phone = None if phone is None or phone.strip() == "" else Data.parse_phone(phone)
                break
            except Exception as e:
                self.print(f"手机号输入错误:{e}")
        while True:
            try:
                address = self.get_input(str, "请输入通讯地址(空格不修改): ")
                address = None if address is None or address.strip() == "" else Data.parse_address(address)
                break
            except Exception as e:
                self.print(f"通讯地址输入错误:{e}")
        if name is None and phone is None and address is None:
            self.print("取消修改！")
        else:
            if name is not None:
                data.name = name
            if phone is not None:
                data.phone = phone
            if address is not None:
                data.address = address
            self.factory.save_data()
            self.print(f"修改成功！\n原数据：{raw_data}\n新数据：{str(data)}")


class QueryMenu(BaseMenu):
    id = 5
    name = "查询联系人"

    def action(self):
        data = self.get_input(str, "请输入编号/姓名/手机号: ")
        if data is None:
            self.print("返回主菜单！")
            return
        if len(data) == 0:
            self.print("返回主菜单！")
            return
        datas = self.factory.search(data)
        if datas is None:
            self.print("未找到联系人！")
        elif isinstance(datas, Data):
            self.print(f"已找到联系人：\n{datas}")
        else:
            self.print(f"已找到联系人：\n{self.factory.type_data(datas)}")


class ExitMenu(BaseMenu):
    id = 6
    name = "退出程序"

    def action(self):
        self.print("退出程序！")
        exit(0)


if __name__ == '__main__':
    try:
        MainMenu(DataFactory("data.json")).run()
    except KeyboardInterrupt:
        BaseMenu.print("\n退出程序~")
