# 批量生成mvp相关代码
# 使用方法：1，安装python3 并添加到环境变量 2，将本文将放到android项目根目录 3，如果要生成MyTestActivity相关文件，则运行 python mvpCreator.py my-test a即可
#          如果要生程度MyTestFragment 则运行 python mvpCreator.py my-test f 即可，后面的a 和 f 是activity和fragment的缩写
# 当前版本：可生成activity文件，fragment文件，presenter文件，view接口文件，activity或者fragment的layout文件，但是还需要自己手动添加svn，将activity添加到
#          androidManifest.xml中，也需要手动调整fragmentComponent和activityComponent
# 后续版本：将当前版本需要手动完成的操作也自动化完成
import os
from sys import argv

script, first, second = argv

template_presenter = r'''
package com.wx.manager.presenter;

import com.wx.manager.base.BasePresenter;
import com.wx.manager.data.local.PreferencesHelper;
import com.wx.manager.di.ConfigPersistent;
import com.wx.manager.view.inter.I${Module}${type}View;
import javax.inject.Inject;
@ConfigPersistent
public class ${Module}${type}Presenter extends BasePresenter<I${Module}${type}View> {

    private PreferencesHelper preferencesHelper;
    @Inject
    public ${Module}${type}Presenter(PreferencesHelper preferencesHelper) {
        this.preferencesHelper = preferencesHelper;
    }

    @Override
    public void attachView(I${Module}${type}View mvpView) {
        super.attachView(mvpView);
    }
}
'''
template_activity = r'''
package com.wx.manager.view.activity;

import android.content.Context;
import android.content.Intent;
import android.os.Build;
import android.os.Bundle;
import com.wx.manager.R;
import com.wx.manager.base.BaseActivity;
import com.wx.manager.di.component.ActivityComponent;
import com.wx.manager.presenter.${Module}${type}Presenter;
import com.wx.manager.view.inter.I${Module}${type}View;
import javax.inject.Inject;

public class ${Module}Activity extends BaseActivity implements I${Module}${type}View {
    @Inject
    ${Module}${type}Presenter ${module}${type}Presenter;

    public static Intent getStartIntent(Context context) {
        Intent intent = new Intent(context, ${Module}Activity.class);
        return intent;
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        initView();
    }


    @Override
    public int getLayout() {
        return R.layout.${module_}_activity;
    }

    @Override
    protected void inject(ActivityComponent activityComponent) {
        activityComponent.inject(this);
    }

    @Override
    protected void attachView() {
        ${module}${type}Presenter.attachView(this);
    }

    @Override
    protected void detachPresenter() {
        ${module}${type}Presenter.detachView();
    }

    private void initView() {
    }
}
'''
template_fragment = r'''
package com.wx.manager.view.fragment;
import android.os.Bundle;
import com.wx.manager.R;
import com.wx.manager.base.BaseFragment;
import com.wx.manager.di.component.FragmentComponent;
import com.wx.manager.presenter.${Module}${type}Presenter;
import com.wx.manager.view.inter.I${Module}${type}View;
import javax.inject.Inject;

public class ${Module}Fragment extends BaseFragment implements I${Module}${type}View {

    @Inject
    ${Module}${type}Presenter ${module}${type}Presenter;

    public static ${Module}Fragment newInstance() {
        return new ${Module}Fragment();
    }

    @Override
    protected int getLayout() {
        return R.layout.${module_}_fragment;
    }

    @Override
    protected void inject(FragmentComponent fragmentComponent) {
        fragmentComponent.inject(this);
    }

    @Override
    protected void attachView() {
        ${module}${type}Presenter.attachView(this);
    }

    @Override
    protected void detachPresenter() {
        ${module}${type}Presenter.detachView();
    }

    @Override
    protected void afterCreate(Bundle savedInstanceState) {
        this.initView();
    }

    private void initView() {
    }
}
'''

template_inter_view = r'''
package com.wx.manager.view.inter;
import com.wx.manager.base.MvpView;

public interface I${Module}${type}View extends MvpView {
}
'''

template_activity_layout = r'''<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:orientation="vertical">


</LinearLayout>

'''
template_fragment_layout = r'''<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content"
    android:orientation="vertical">


</LinearLayout>

'''


def upper_first(name):
    first = name[0:1]
    rest = name[1:]
    return first.upper() + rest


def lower_first(name):
    first = name[0:1]
    rest = name[1:]
    return first.lower() + rest


def is_file_exits(path):
    if os.path.exists(path):
        raise RuntimeError(path + 'exits!')


def check_param(name, type):
    if (type != 'a' and type != 'f'):
        raise RuntimeError('type is only a or f')


def check_folder(path):
    if not os.path.exists(path):
        os.makedirs(path)


def get_java_file_name(name):
    arr = name.split('-')
    ret = ''
    for value in arr:
        ret += upper_first(value)
    return ret


def get_java_file_name_lower_first(name):
    arr = name.split('-')
    ret = ''
    for value in arr:
        ret += upper_first(value)
    temp = ret[0:1]
    rest = ret[1:]
    return temp.lower() + rest


def get_layout_file_name(name):
    ret = name.replace('-', '_')
    return ret


def indent(elem, level=0):
    i = "\n" + level * "    "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "    "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


def update_android_manifest(activity_name):
    abs_path = os.path.abspath('.')
    manifest_file_path = os.path.join(
        abs_path, 'app/src/main/AndroidManifest.xml')
    insert_str = '\t\t<activity android:name=".view.activity.' + activity_name + '" />\n'
    contents = []
    target_index = 0
    with open(manifest_file_path) as manifest_file:
        for line in manifest_file.readlines():
            contents.append(line)
    for line in contents:
        if ('</application>' in line):
            target_index = contents.index(line)
    if target_index != 0:
        contents.insert(target_index, insert_str)
    with open(manifest_file_path, 'w') as manifest_file:
        for line in contents:
            manifest_file.write(line)


def update_activity_component(activity_name):
    abs_path = os.path.abspath('.')
    activity_component_path = os.path.join(abs_path,
                                           'app/src/main/java/com/wx.manager/di/component/ActivityComponent.java')
    contents = []
    with open(activity_component_path) as a_component_file:
        for line in a_component_file.readlines():
            contents.append(line)
    inject_content = '\tvoid inject(' + activity_name + \
        ' ' + lower_first(activity_name) + ');\r'
    import_content = 'import com.wx.manager.view.activity.' + activity_name + ';\r'
    inject_index = 0
    import_index = 0
    for line in contents:
        if ('package' in line):
            import_index = contents.index(line) + 1
        if ('ActivityComponent' in line):
            inject_index = contents.index(line) + 1
    if inject_index != 0:
        contents.insert(inject_index, inject_content)
    contents.insert(import_index, import_content)
    with open(activity_component_path, 'w') as a_component_file:
        for line in contents:
            a_component_file.write(line)


def update_fragment_component(fragment_name):
    abs_path = os.path.abspath('.')
    fragment_component_path = os.path.join(abs_path,
                                           'app/src/main/java/com/wx.manager/di/component/FragmentComponent.java')
    contents = []
    with open(fragment_component_path) as f_component_file:
        for line in f_component_file.readlines():
            contents.append(line)
    inject_content = '\tvoid inject(' + fragment_name + \
        ' ' + lower_first(fragment_name) + ');\r'
    import_content = 'import com.wx.manager.view.fragment.' + fragment_name + ';\r'
    import_index = 0
    inject_index = 0
    for line in contents:
        if ('package' in line):
            import_index = contents.index(line) + 1
        if ('FragmentComponent' in line):
            inject_index = contents.index(line) + 1
    if inject_index != 0:
        contents.insert(inject_index, inject_content)
    contents.insert(import_index, import_content)
    with open(fragment_component_path, 'w') as f_component_file:
        for line in contents:
            f_component_file.write(line)


def generate_file(name, type):
    check_param(name, type)
    abs_path = os.path.abspath('.')
    parent_folder_path = os.path.join(
        abs_path, 'app/src/main/java/com/wx.manager')
    res_layout_folder_path = os.path.join(abs_path, 'app/src/main/res/layout')
    presenter_floder_path = os.path.join(parent_folder_path, 'presenter')
    activity_folder_path = os.path.join(parent_folder_path, 'view/activity')
    fragment_folder_path = os.path.join(parent_folder_path, 'view/fragment')
    view_folder_path = os.path.join(parent_folder_path, 'view/inter')

    check_folder(parent_folder_path)
    check_folder(res_layout_folder_path)
    check_folder(presenter_floder_path)
    check_folder(activity_folder_path)
    check_folder(fragment_folder_path)
    check_folder(view_folder_path)

    presenter_file_path = presenter_floder_path + '/' + \
        get_java_file_name(name) + type.upper() + 'Presenter.java'
    view_file_path = view_folder_path + '/' + 'I' + \
        get_java_file_name(name) + type.upper() + 'View.java'
    with open(view_file_path, 'w') as view_file:
        temp = template_inter_view.replace('${Module}', get_java_file_name(name)) \
            .replace('${module}', get_java_file_name_lower_first(name)).replace('${type}', type.upper())
        view_file.write(temp)
    with open(presenter_file_path, 'w') as presenter_file:
        temp = template_presenter.replace('${Module}', get_java_file_name(name)) \
            .replace('${module}', get_java_file_name_lower_first(name)) \
            .replace('${type}', type.upper())
        presenter_file.write(temp)
    if type == 'a':
        a_layout_file = res_layout_folder_path + '/' + \
            get_layout_file_name(name) + '_activity.xml'
        activity_file_path = activity_folder_path + '/' + \
            get_java_file_name(name) + 'Activity.java'
        with open(activity_file_path, 'w') as activity_file:
            temp = template_activity.replace('${Module}', get_java_file_name(name)) \
                .replace('${module}', get_java_file_name_lower_first(name)) \
                .replace('${type}', type.upper()) \
                .replace('${module_}', get_layout_file_name(name))
            activity_file.write(temp)
        with open(a_layout_file, 'w') as a_layout_file:
            a_layout_file.write(template_activity_layout)
        update_android_manifest(get_java_file_name(name) + 'Activity')
        update_activity_component(get_java_file_name(name) + 'Activity')
    if type == 'f':
        f_layout_file = res_layout_folder_path + '/' + \
            get_layout_file_name(name) + '_fragment.xml'
        fragment_file_path = fragment_folder_path + '/' + \
            get_java_file_name(name) + 'Fragment.java'
        with open(fragment_file_path, 'w') as fragment_file:
            temp = template_fragment.replace('${Module}', get_java_file_name(name)) \
                .replace('${module}', get_java_file_name_lower_first(name)) \
                .replace('${type}', type.upper()) \
                .replace('${module_}', get_layout_file_name(name))
            fragment_file.write(temp)
        with open(f_layout_file, 'w') as f_layout_file:
            f_layout_file.write(template_fragment_layout)
        update_fragment_component(get_java_file_name(name) + 'Fragment')


if __name__ == '__main__':
    generate_file(first, second)
