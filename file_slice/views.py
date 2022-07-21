import shutil
import json
from django.shortcuts import render
from django.http import JsonResponse
from django.http import HttpResponse
import os

FILE_PATH = './file_slice/file'
HTTP_400 = HttpResponse({
    'code': 400,
    'msg': 'klw sb'
})


# is_path_exists 判断路径是否存在
#   存在 True
#   不存在 False
def is_path_exists(path):
    return os.path.exists(path.strip().rstrip("\\"))  # 去除首位空格 去除尾部 \ 符号


# file_mkdir 创建路径
# 如果不存在则创建目录
def file_mkdir(path):
    if not is_path_exists(path):
        os.makedirs(path)


# 判断字符串是否为整形数字
def str_is_int(str_):
    try:
        int(str_)
        return True
    except ValueError:
        return False


# get_path_chunks 获取路径下的所有切片
def get_path_chunks(path):
    file_list = os.listdir(path)
    return list(filter(lambda name: len(name.split('.')) == 1 and str_is_int(name), file_list))  # 筛选出切片文件 去掉其它文件


# get_chunks_info 获取该文件上传情况
# params
#   file_hash 文件哈希 必填
#   name 文件名 必填
# return
#   EXISTS 说明该文件已经上传过了且合并成功了 不需要执行后面的逻辑了
#   get_path_chunks(path) 说明该文件有0个或多个切片 前端需要上传未上传的切片
def get_chunks_info(request):
    if request.method != 'GET':
        return HTTP_400
    file_hash = request.GET.get('file_hash')
    name = request.GET.get('name')
    path = FILE_PATH + '/' + file_hash
    file_mkdir(path)
    file_list = os.listdir(path)
    if name in file_list:
        return JsonResponse({
            'code': 'ok',
            'msg': 'EXISTS'
        }, status=200)
    else:
        return JsonResponse({
            'code': 'ok',
            'msg': get_path_chunks(path)
        }, status=200)


# accept_file_chunk 接受文件切片
# params
#   file_chunk  文件切片  必填
#   chunk_index 切片下标  必填
#   file_hash 文件哈希    必填
def accept_file_chunk(request):
    if request.method != 'POST':
        return HTTP_400
    file_chunk = request.FILES.get('file_chunk')
    chunk_index = request.POST.get('chunk_index')
    file_hash = request.POST.get('file_hash')
    save_chunk(file_chunk, chunk_index, file_hash)
    return JsonResponse({
        'code': 200,
        'msg': chunk_index
    })


# save_chunk 存储切片
# params
#   chunk 文件切片
#   index 切片下标
#   hash_ 文件哈希
def save_chunk(chunk, index, hash_):
    path = FILE_PATH + '/' + hash_
    file_mkdir(path)
    with open(path + '/' + index, 'wb+') as f:
        for c in chunk:
            f.write(c)


# merge_file_chunk 合并文件夹里的切片
# params
#   file_hash 文件哈希 必填
#   name 文件名 必填
#   chunk_number 切片数量 必填
def merge_file_chunk(request):
    if request.method != 'GET':
        return HTTP_400
    file_hash = request.GET.get('file_hash')
    name = request.GET.get('name')
    chunk_number = request.GET.get('chunk_number')
    path = FILE_PATH + '/' + file_hash
    if not is_path_exists(path):
        return HTTP_400
    chunk_index_list = get_path_chunks(path)
    if int(chunk_number) != len(chunk_index_list):
        return JsonResponse({
            'code': 401,
            'msg': '合并失败'
          }, status=401)
    chunk_list = []
    index = 0
    while index < len(chunk_index_list):
        with open(path + '/' + str(index), 'rb+') as f:
            chunk_list.append(f.read())
        index += 1
    shutil.rmtree(path)
    file_mkdir(path)
    with open(path + '/' + name, 'wb+') as f:
        for chunk in chunk_list:
            f.write(chunk)
    return JsonResponse({
        'code': 200,
        'msg': 'merge ok'
    }, status=200)
