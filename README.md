# shuLibrary

上海大学图书馆手机版后端

## 安装依赖

需要Python3：

```shell
pip3 install -r requirements.txt
```

## 需要自行安装的依赖

- redis

## 运行

运行前请确保redis-server正在工作，可通过app.py中的app.config['REDIS_KWARGS']参数调整host和port（默认为127.0.0.1:6379）

### 开发环境

```shell
export FLASK_APP=app
flask run
```

### 生产环境

```shell
gunicorn -b 0.0.0.0:5000 app:app
```

## API Reference

### 登录

#### Request

- method: `POST`
- URL: `/login`
- Format: `json`
- Body: 
  ```json
  {
      "username": "学生证号",
      "password": "学生密码"
  }
  ```

#### Response

```json
{
    "token": "$JWT_TOKEN"
}
```

### 借阅信息

#### Request

- method: `GET`
- URL: `/loans`
- Authorization: `Bearer $JWT_TOKEN`

#### Response

```json
{
    "loans": [
        {
            "author": "著者",
            "description": "题名",
            "due_date": "应还日期(YYYYMMDD)",
            "fine": "罚金",
            "id": "ID",
            "sub_library": "分馆",
            "year": "出版年(YYYY)"
        },
        "..."
    ]
}
```

### 借阅历史

#### Request

- method: `GET`
- URL: `/histories`
- Authorization: `Bearer $JWT_TOKEN`

#### Response

```json
{
    "histories": [
        {
            "author": "著者",
            "description": "题名",
            "due_date": "应还日期(YYYYMMDD)",
            "fine": "罚金",
            "returned_date": "归还日期(YYYYMMDD)",
            "returned_hour": "归还时间(HH:MM)",
            "sub_library": "分馆",
            "year": "出版年(YYYY)"
        },
        "..."
    ]
}
```
