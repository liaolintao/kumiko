import onyx_img_utils

dir = 'C:\onyx\github\python\kumiko\comic-raw'

files = onyx_img_utils.listAllFile(dir)
for file in files:
    onyx_img_utils.saveScaleImg(file)

