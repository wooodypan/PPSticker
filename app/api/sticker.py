from flask import jsonify, request, g, current_app, url_for, \
send_from_directory,redirect
from . import api
from .. import db
from ..models import User, Sticker, Permission
from .decorators import permission_required
from werkzeug.utils import secure_filename#上传图片用
from werkzeug.datastructures import FileStorage
import os,hashlib
from datetime import datetime
from requests import post,get
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
        ppurl = request.form['ppurl']
        file = None
        extension = ''
        current_time = str(datetime.now().strftime('%Y-%m-%d_%H.%M.%S_%f')[:-3])
        if len(request.files):
            file = request.files['ppFiles']
        else:
            extension = ppurl.split('.')[-1]
            filename = current_time + '.' + extension
            absolute_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            downloadFileWithRequests(ppurl, absolute_path)
            with open(absolute_path, 'rb') as fp:
                file = FileStorage(fp)
        pptag = request.form['pptag']
        pptag = pptag.replace('，',',').strip()#替换逗号去空格
        width = request.form['width']
        height = request.form['height']
        fileSize = request.form['fileSize']
        if file and allowed_file(file.filename):
            # filename = secure_filename(file.filename)
            # filename = "."+filename if "." not in filename else filename
            extension = file.mimetype.split('/')[1] if len(extension) < 2 else extension
            filename = current_time +'.' + extension
            absolute_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            if ppurl and len(ppurl)>1:
                pass
                # downloadFileWithRequests(ppurl, absolute_path)
            else:
                file.save(absolute_path)#一定要提前创建文件夹！
            fileSize = os.stat(absolute_path).st_size
            # file.remove
            # return '{"code":200}' 34fa38284dfe7219e0392c11da505498
            img_hash = md5_file(absolute_path)
            # img_hash2 = hashlib.md5(file.read()).hexdigest() #错误
            
            # encoding = 'utf-8'
            # b'hello'.decode(encoding)
            fileExists = Sticker.query.filter_by(sid=img_hash).first()
            if fileExists is None:
                small_image = handleBigImage(absolute_path,fileSize)
                # smmsURL = SMMSImage.upload(image=absolute_path)
                currentUser = g.current_user
                newSticker = Sticker(sid=img_hash,
                                     owner_id=currentUser.id,
                                     tag=pptag,
                                     width=width,
                                     height=height,
                                     fileSize=fileSize,
                                     sinaURL=ppurl,
                                     thumbnail=small_image,
                                     url= filename)#request.path.replace('addsticker','uploadimg')+filename)
                db.session.add(newSticker)#host_url origin
                db.session.commit()
                return redirect(url_for('api.uploaded_file',filename=filename))
            else:
                os.remove(absolute_path)
                # 如果您使用的是蓝图，则url_for应该这样调用：url_for（'blueprint_name.func_name'）
                # return fileExists.to_json()
                return jsonify(fileExists.to_json()), 201, {'msg': '你丫的已经上传过了'}
    # json = request.json
    # return jsonify(post.to_json()), 201, {'Location': url_for('api.get_post', id=post.id, _external=True)}
#制作略缩图
def handleBigImage(fileName,fileSize):
    extension = fileName.split('.')[-1]
    name = fileName[:-len(extension)-1]
    small_image = ''
    print('===类型'+extension)
    if len(extension)<3:
    	return small_image
	#大于128K的图片做略缩图
    if int(fileSize) > 128*1024:
        if extension == 'gif':
            small_image = name+"_thumb"+".jpg"
            os.system("convert -coalesce  '"+fileName+"[0]'  -resize '100x100>' "+small_image)
            return small_image.split('/')[-1]
        elif extension == 'jpg' or extension == 'jpeg' or extension == 'png':
            small_image = name+"_thumb."+extension
            os.system("convert -coalesce  '"+fileName+"'  -resize '100x100>' "+small_image)
            return small_image.split('/')[-1]
        else:
        	#小图不处理了
            pass
    return small_image

#服务器下载图片
def downloadFileWithRequests(url, file_name):
    # open in binary mode
    with open(file_name, "wb") as file:
        # get request
        response = get(url)
        # write to file
        file.write(response.content)
# 图片生成md5值作为唯一ID
def md5_file(file_path):
    md5_obj = hashlib.md5()
    with open(file_path, 'rb') as file_obj:
        md5_obj.update(file_obj.read())
    file_md5_id = md5_obj.hexdigest()
    return file_md5_id
# 文件访问
@api.route('/uploadimg/<filename>')
def uploaded_file(filename):
    print('==========')
    return send_from_directory(current_app.config['UPLOAD_FOLDER'],
                               filename)        


@api.route('/indexs')
def stickerindex():
    return current_app.send_static_file('s.html')
# http://127.0.0.1:5000/api/v1/users/12345/sticker
# http://p.agolddata.com/sticker/api/v1/user/12345/sticker
# http://p.agolddata.com/api/v1/user/12345
# http://p.agolddata.com/sticker
# http://127.0.0.1:5000/api/v1/users/12345/sticker

# @api.route('/users/<username>/sticker/')
# def get_user_stickers(username):
@api.route('/users/sticker/')
def get_user_stickers():
    print('=====get_user_stickers=====')
    currentUser = g.current_user
    user = User.query.filter_by(username=currentUser.username).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = user.stickers.order_by(Sticker.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_user_stickers', id=id, page=page-1,
                       _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_user_stickers', id=id, page=page+1,
                       _external=True)
    return jsonify({
        'stickers': [post.to_json() for post in posts],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })
    

# http://127.0.0.1:5000/sticker/api/v1/searchsticker/?searchText=%E5%8D%A7%E6%A7%BD
@api.route('/searchsticker/')
def search_user_stickers():
    print('=====get_user_stickers=====')
    currentUser = g.current_user
    user = User.query.filter_by(username=currentUser.username).first_or_404()
    page = request.args.get('page', 1, type=int)
    count = 10
    page_num = (page-1) * count
    search_text = request.args.get('searchText', ' ', type=str)
    # if
    pagination = Sticker.query.filter(Sticker.tag.contains(search_text)).offset(page_num).limit(count).all()
    return jsonify({
        'stickers': [stk.to_json() for stk in pagination]
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