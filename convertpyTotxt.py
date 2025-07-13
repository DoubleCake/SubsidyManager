import os
import shutil

def convert_py_to_txt_and_move(ignore_dirs, dest_dir):
    """
    遍历当前目录下所有非忽略路径中的 .py 文件，
    并将它们复制为同名 .txt 文件，存放到目标目录。
    
    :param ignore_dirs: 完整路径的忽略目录列表
    :param dest_dir: 输出目标文件夹路径
    """
    current_dir = os.getcwd()

    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    # 规范化 ignore_dirs 为绝对路径
    ignore_abs_dirs = [os.path.abspath(d) for d in ignore_dirs]

    print(f"当前工作目录: {current_dir}")
    print(f"忽略目录: {ignore_abs_dirs}")
    print(f"输出目录: {dest_dir}")

    for root, dirs, files in os.walk(current_dir):
        # 判断当前 root 是否在忽略目录中
        current_root_abs = os.path.abspath(root)

        # 如果当前目录是忽略目录或其子目录，则跳过
        should_skip = any(
            current_root_abs.startswith(ignore_dir.rstrip('/') + os.sep) or current_root_abs == ignore_dir
            for ignore_dir in ignore_abs_dirs
        )

        if should_skip:
            print(f"跳过目录: {root}")
            continue

        for file in files:
            if file.endswith('.py'):
                src_file = os.path.join(root, file)
                txt_name = os.path.splitext(file)[0] + '.txt'
                dest_file = os.path.join(dest_dir, txt_name)

                # 如果存在同名文件，可以选择覆盖或者跳过
                if os.path.exists(dest_file):
                    print(f"已存在: {dest_file}，跳过。")
                    continue

                shutil.copy(src_file, dest_file)
                print(f"已复制: {src_file} -> {dest_file}")

if __name__ == '__main__':
    # 设置需要忽略的完整路径目录（可多个）
    ignore_directories = [
        'venv',
        'utils',  # 比如你不想处理 utils 目录下的 py 文件
        '__pycache__',  # 忽略 Python 缓存目录
        'PyQt-Fluent-Widgets-PySide6',
    ]

    # 把上面的相对路径转换成绝对路径
    ignore_directories = [os.path.abspath(d) for d in ignore_directories]

    output_folder = os.path.join(os.getcwd(), 'converted_txt_files')

    # 清空旧的输出目录（可选）
    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)
    os.makedirs(output_folder)

    convert_py_to_txt_and_move(ignore_directories, output_folder)