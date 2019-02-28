import xlrd

import xlrd

# 打开文档
book = xlrd.open_workbook("/home/ingin/Desktop/aa/a.xls")

# print("The number of worksheets is", book.nsheets)
# print("Worksheet name(s):", book.sheet_names())

# 打开工作表(三种方法)
# sh = book.sheet_by_index(0)
sh = book.sheets()[0]
# sh = book.sheet_by_name('sheet1')
#
# # 操作行列和单元格
# print(sh.name, sh.nrows, sh.ncols)
# print("Cell D30 is", sh.cell_value(rowx=29, colx=3))
# print "Cell D30 is", sh.cell(29,3).value
#
# # 循环
for rx in range(1):
    # print(type(sh.row(rx)))
    for i in sh.row(rx):
        print(type(i))
        print(i.value)
# Refer to docs for more details.
# Feedback on API is welcomed.



"""
项目名
项目说明
需要远程部署的路径
包含的服务 多个
服务名
服务说明

服务的版本号
版本说明
服务路径   项目名/服务名
服务配置文件的路径
服务的多个配置项{1.2.3}
服务的依赖服务名及版本号{1,2,3}

"""