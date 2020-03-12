from flask import jsonify, request, g, current_app, url_for, \
send_from_directory,redirect
from . import api
from .. import db
from ..models import User, Sticker, Permission
from .decorators import permission_required
from werkzeug.utils import secure_filename#上传图片用
import os,hashlib
from datetime import datetime
from requests import post #,get
from json import loads



ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
           
# https://i.loli.net/2020/03/10/Cg27IaZuLXh5w6O.jpg
# https://i.loli.net/2020/03/11/GNKHg1mYxje2vfo.jpg     贵宾一位
# https://i.loli.net/2020/03/11/7POTYFA8QGbJVHX.png  不懂，再见
# http://127.0.0.1:5000/api/v1/addsticker
# 文档参考 https://flask.palletsprojects.com/en/1.1.x/patterns/fileuploads/
@api.route('/addsticker/', methods=['POST'])
# @permission_required(Permission.WRITE_ARTICLES)
def addsticker():
    print('=====addsticker=====')
    if request.method == 'POST':
        file = request.files['ppFiles']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filename = "."+filename if "." not in filename else filename
            filename = str(datetime.now().strftime('%Y-%m-%d_%H_%M_%S.%f')[:-3]) + filename 
            absolute_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(absolute_path)
            # return '{"code":200}' 34fa38284dfe7219e0392c11da505498
            img_hash = md5_file(absolute_path)
            # img_hash = hashlib.md5(file.read()).hexdigest() 
            fileExists = Sticker.query.filter_by(sid=img_hash).first()
            if fileExists is None:
                # smmsURL = SMMSImage.upload(image=absolute_path)
                newSticker = Sticker(sid=img_hash,url= request.path+filename)
                db.session.add(newSticker)#host_url origin
                db.session.commit()
                return redirect(url_for('api.uploaded_file',filename=filename))
            else:
                # 如果您使用的是蓝图，则url_for应该这样调用：url_for（'blueprint_name.func_name'）
                return fileExists.to_json()
    # json = request.json
    # return jsonify(post.to_json()), 201, {'Location': url_for('api.get_post', id=post.id, _external=True)}
    
# 图片生成md5值作为唯一ID
def md5_file(file_path):
    md5_obj = hashlib.md5()
    with open(file_path, 'rb') as file_obj:
        md5_obj.update(file_obj.read())
    file_md5_id = md5_obj.hexdigest()
    return file_md5_id
# 文件访问
@api.route('/uploads/<filename>')
def uploaded_file(filename):
    print('==========')
    return send_from_directory(current_app.config['UPLOAD_FOLDER'],
                               filename)        

# http://127.0.0.1:5000/api/v1/users/12345/sticker
# http://p.agolddata.com/sticker/api/v1/user/12345/sticker
# http://p.agolddata.com/api/v1/user/12345
# http://p.agolddata.com/sticker
# http://127.0.0.1:5000/api/v1/users/12345/sticker
@api.route('/users/<int:id>/sticker/')
def get_user_sticker(id):
    print('=====user=====2')
    
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = user.posts.order_by(Sticker.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_user_posts', id=id, page=page-1,
                       _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_user_posts', id=id, page=page+1,
                       _external=True)
    return jsonify({
        'posts': [post.to_json() for post in posts],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })
    
    
    
    
class SMMSImage(object):
    #https://github.com/skycity233/SMPIC/blob/67ea54f5ba2f9c1e787ca4de1b0cba0e990597cb/Smms.py
    @classmethod
    def upload(cls, image, token=None):
        """
        图片上传接口。
        :param image: 图片的地址
        :param token: API Token
        :return: 返回图片上传后的URL
        """
        url = 'https://sm.ms/api/v2/upload'
        params = {'format': 'json', 'ssl': True}
        files = {'smfile': open(image, 'rb')}
        headers = {'Authorization': token}
        if token:
            re = post(url, headers=headers, files=files, params=params)
        else:
            re = post(url, files=files, params=params)
        #{"success":true,"code":"success","message":"Upload success.","data":{"file_id":0,"width":240,"height":219,"filename":"2020-03-11_19_45_19.1498a8f318736a6cf3b456b467875931f0d.png","storename":"7POTYFA8QGbJVHX.png","size":21692,"path":"\\/2020\\/03\\/11\\/7POTYFA8QGbJVHX.png","hash":"MmPjykCzOZtAX1u5Jls9Y4dErI","url":"https:\\/\\/i.loli.net\\/2020\\/03\\/11\\/7POTYFA8QGbJVHX.png","delete":"https:\\/\\/sm.ms\\/delete\\/MmPjykCzOZtAX1u5Jls9Y4dErI","page":"https:\\/\\/sm.ms\\/image\\/7POTYFA8QGbJVHX"},"RequestId":"14A8EAEC-B2EF-4117-99F2-9DA387EAEAFE"}
        re_json = loads(re.text)
        try:
            if re_json['success']:
                return re_json['data']['url']
            else:
                return re_json['images']
        except KeyError:
            if re_json['code'] == 'unauthorized':
                raise ConnectionRefusedError
            if re_json['code'] == 'flood':
                raise ConnectionAbortedError