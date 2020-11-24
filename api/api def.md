### login

登录返回user_id，然后通过fetch_rec_list得到默认的推荐item

输入参数：

* user_name String 类型

* gender String 类型 M代表男 F代表女

* age int 类型

* occupation String 类型 范围如下：

  * ```
    0 “other” or not specified
    1 “academic/educator”
    2 “artist”
    3 “clerical/admin”
    4 “college/grad student”
    5 “customer service”
    6 “doctor/health care”
    7 “executive/managerial”
    8 “farmer”
    9 “homemaker”
    10 “K-12 student”
    11 “lawyer”
    12 “programmer”
    13 “retired”
    14 “sales/marketing”
    15 “scientist”
    16 “self-employed”
    17 “technician/engineer”
    18 “tradesman/craftsman”
    19 “unemployed”
    20 “writer”
    ```

* tags list 类型 是用户的兴趣标签

输入举例：

```json
{
  'username':'cliff',
  'gender':'M',
  'age':45,
  'occupation':'CTO',
  'tags':['XA','XB'] // tag list 预定义，写死在页面上，用户选择后，以 list 方式返回
}
```

输出举例

```json
{
  'user_id' : 123, // 
  'return' : 0 // 0 代表succeed 1代表 failed
}
```

### fetch_rec_list

输入参数：

* user_id

输出举例：

```json
// 废弃，按照👇的那个来提供
{ 
  'item_list': [33, 34, 56], // 需要通过 get_item_title 获取新闻的标题
  'return' : 0, // 0 代表succeed 1代表 failed
  'state': [0,1,0] // 0 代表冷启，1代表推荐
}
```

或者：

```json
{
  'item_list': [{'item_id':33,'type':0,'title':'this is title1'},{'item_id':34,'type':1,'title':'title 2'}],
  'return' : 0, // 0 代表succeed 1代表 failed
}
```



### click 

click 后界面不刷新，但是要弹出小窗，**<u>小窗内容待定</u>**，[参考GitHub](https://github.com/hardikvasa/google-images-download) 并向服务器发送click 事件

输入参数：

* user_id ：login 返回的 user_id
* item_id 

输入举例：

```json
{
  'user_id': 321,
  'item_id':333
}
```

输出举例：

```json
{
  'return' : 0 // 0 代表succeed 1代表 failed
}
```

### get_item_content

弹窗展示的内容

输入参数：

* item_id

输出举例：

```json
{
  'item_pic_url':['url1,jpg','url2.jpg'],
  'return' : 0 // 0 代表succeed 1代表 failed
}
```

GitHub [新闻标题](https://github.com/hwwang55/DKN/blob/master/data/news/raw_train.txt)

