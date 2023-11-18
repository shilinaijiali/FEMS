// datatabel定义
dt = {
    "bAutoWidth": true,//自动宽度
    "scrollCollapse": true, // 高度自适应
    "bFilter": false, //过滤功能
    "bLengthChange": false, //改变每页显示数据数量
    'iDisplayLength': 10, //用于指定当DataTable设置为滚动时，最多可以一屏显示多少条数据
    // "sScrollY": '300px', //是否开启垂直滚动，以及指定滚动区域大小
    'responsive': true, // Enable responsive design 实现响应式设计
    'hover': true, // Enable hover effects 启动悬停效果
    'order': [],  //给[]，禁用排序
};

checkbox_dt = {
    "bAutoWidth": false,//自动宽度
    "scrollCollapse": true, // 高度自适应
    "bFilter": false, //过滤功能
    "bLengthChange": false, //改变每页显示数据数量
    'iDisplayLength': 10, //用于指定当DataTable设置为滚动时，最多可以一屏显示多少条数据
    // "sScrollY": '300px', //是否开启垂直滚动，以及指定滚动区域大小
    'responsive': true, // Enable responsive design 实现响应式设计
    'hover': true, // Enable hover effects 启动悬停效果
    // 'order': [[1, 'asc']], // Enable sorting by the first column in ascending order 启用按第一列升序排序
    'columnDefs': [{
        targets: 0,
        data: null,
        className: 'text-center',
        defaultContent: "<input type ='checkbox' name='head_list' value=''>",
    },],
};

checkbox_dt_with_export_excel = {
    "bAutoWidth": false,//自动宽度
    "scrollCollapse": true, // 高度自适应
    "bFilter": false, //过滤功能
    "bLengthChange": false, //改变每页显示数据数量
    'iDisplayLength': 10, //用于指定当DataTable设置为滚动时，最多可以一屏显示多少条数据
    // "sScrollY": '300px', //是否开启垂直滚动，以及指定滚动区域大小
    'responsive': true, // Enable responsive design 实现响应式设计
    'hover': true, // Enable hover effects 启动悬停效果
    // 'order': [[1, 'asc']], // Enable sorting by the first column in ascending order 启用按第一列升序排序
    'order': [],  //给[]，禁用排序
    dom: 'Bfrtip',
    buttons: [
        'excelHtml5'
    ],
    'columnDefs': [{
        targets: 0,
        data: null,
        className: 'text-center',
        defaultContent: "<input type ='checkbox' name='head_list' value=''>",
    },],
};

// datatabel定义
simple_dt = {
    "bAutoWidth": true,//自动宽度
    "scrollCollapse": true, // 高度自适应
    "bFilter": false, //过滤功能
    "bLengthChange": false, //改变每页显示数据数量
    'iDisplayLength': 10, //用于指定当DataTable设置为滚动时，最多可以一屏显示多少条数据
    // "sScrollY": '300px', //是否开启垂直滚动，以及指定滚动区域大小
    'responsive': true, // Enable responsive design 实现响应式设计
    'hover': true, // Enable hover effects 启动悬停效果
    'order': [[0, 'asc']],  //第一列降序排序
    'paging': false, //禁用翻页功能
    'info': false //禁用表格底部的“Showing x to y of z entries”信息
};

// datatabel定义
modal_dt = {
    "bAutoWidth": true,//自动宽度
    "scrollCollapse": true, // 高度自适应
    'responsive': true, // Enable responsive design 实现响应式设计
    'hover': true, // Enable hover effects 启动悬停效果
    "ordering": false, // Disable ordering and remove sort icons
    'paging': false, //禁用翻页功能
    'info': false, //禁用表格底部的“Showing x to y of z entries”信息
    'columnDefs': [
        {
            'targets': '_all',
            'className': 'text-center',
        }
    ]
};


// 将数据显示在datatable上, 新增勾选框
function list_to_dt_data_checkbox0(dt_obj, dt_data_list, clear) {
    if (clear === 'clear') {
        dt_obj.clear().draw()
    }
    for (let i = 0; i < dt_data_list.length; i++) {
        const temp_list = [''];
        const c = temp_list.concat(dt_data_list[i]);
        dt_obj.row.add(c).draw()
    }
}

// input 批量設置爲只讀屬性
function set_attr_readonly(readonly_list) {
    for (const inp in readonly_list) {
        const input_id = '#' + readonly_list[inp];
        $(input_id).attr('readOnly', true)
        // $(input_id).style.border = "#53ff4cbd";
        $(input_id).css("background-color", "rgba(255,138,138,0.74)");
    }
}

// input 批量赋值
function set_input_values(data_list, id_list) {
    for (let i = 0; i < id_list.length; i++) {
        const id = '#' + id_list[i];
        $(id).val(data_list[i])
    }
}


// input 批量設置為空
function set_val_empty(val_empty_list) {
    for (const inp in val_empty_list) {
        const input_id = '#' + val_empty_list[inp];
        $(input_id).val('')
    }
}


//获取tbody中所有行的值，返回一个二维列表
function get_table_rows_data(tbody_id) {
    var rows_list = []
    var tbody_id = '#' + tbody_id
    $(tbody_id)
        .find('tr')
        .each(function () {
            var temp_row_list = []
            $(this)
                .find('td')
                .each(function () {
                    var txt = $(this).html()
                    if (txt == 'No data available in table') {
                        return false
                    } else {
                        temp_row_list.push($(this).html())
                    }
                })
            if (temp_row_list.length > 0) {
                rows_list.push(temp_row_list)
            }
        })
    return rows_list
}

// 获取tbody中选中行的值，返回一个二维列表
function get_table_rows_data_chosen(tbody_id) {
    const rows_list = []
    const tbody = '#' + tbody_id
    $(tbody)
        .find('input[type=checkbox]')
        .each(function () {
            const temp_row_list = [];
            if ($(this).is(':checked')) {
                const td_ele1 = $(this).parent();
                td_ele1.prevAll().each(function () {
                    temp_row_list.push($(this).html())
                })
                td_ele1.nextAll().each(function () {
                    temp_row_list.push($(this).html())
                })
            }

            if (temp_row_list.length > 0) {
                rows_list.push(temp_row_list)
            }
        })
    return rows_list
}

// 将数据显示在datatable上, 新增id
function list_to_dt_data_add_id(dt_obj, dt_data_list, clear) {
    if (clear === 'clear') {
        dt_obj.clear().draw()
    }
    for (let i = 0; i < dt_data_list.length; i++) {
        const data = [i + 1].concat(dt_data_list[i]);
        dt_obj.row.add(data).draw();
    }
}

// 将数据显示在datatable上
function list_to_dt_data(dt_obj, dt_data_list, clear) {
    if (clear === 'clear') {
        dt_obj.clear().draw()
    }
    for (let i = 0; i < dt_data_list.length; i++) {
        dt_obj.row.add(dt_data_list[i]).draw();
    }
}

// 自定义消息弹窗
function myAlert(message, type = 'info', duration) {
    // 检查是否存在旧弹窗并移除
    const oldAlertDiv = document.querySelector("#alertDiv");
    if (oldAlertDiv) {
        oldAlertDiv.remove();
    }

    // 创建包含弹窗的 div 元素
    const alertDiv = document.createElement("div");
    alertDiv.id = "alertDiv";
    alertDiv.classList.add("alert", "mt-3", "alert-primary", "alert-dismissible", "fade", "show");

    // 设置弹窗的类型和背景颜色,当类型为success给一个自动关闭的时间，success弹窗代表当前操作成功
    if (type === "success") {
        alertDiv.classList.add("alert-success");
        // duration = 5000
        //  warning弹窗背景色为橘色，将warning作为系统异常
    } else if (type === "warning") {
        alertDiv.classList.add("alert-warning");
        //  alter-info 是提示消息弹窗
    } else if (type === "info") {
        alertDiv.classList.add("alert-info");
        // duration = 5000
        //  danger弹窗背景色为红色，将danger作为操作错误
    } else if (type === "danger") {
        alertDiv.classList.add("alert-danger");
    }

    // 去掉弹窗的四个角的尖锐感
    alertDiv.classList.add("rounded-0");


    // 设置弹窗的内容和关闭按钮
    alertDiv.innerHTML = `
    <div id="alter"  class="d-flex justify-content-between align-items-center">
      <div>${message}</div>
      <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    </div>
  `;

    // 设置弹窗的 z-index
    alertDiv.style.zIndex = "99";

    // 将弹窗添加到 card-header 中
    const cardHeader = document.querySelector(".card-header");
    cardHeader.style.position = "relative";
    cardHeader.appendChild(alertDiv);

    // 自动关闭弹窗
    if (duration) {
        setTimeout(() => {
            alertDiv.remove();
        }, duration);
    }

}


/**
 * 防止重複請求
 * @param key 按鍵id
 * @param callback 执行的函数
 */
let ongoingRequests = {};

function preventDuplicateRequests(key, callback) {
    // 如果当前按键对应的请求正在进行中，则直接返回，不执行回调函数
    if (ongoingRequests[key]) {
        return;
    }
    // 标记当前按键对应的请求正在进行中
    ongoingRequests[key] = true;
    // 执行回调函数，并在请求完成后从ongoingRequests中删除当前按键对应的请求
    callback().finally(() => {
        delete ongoingRequests[key];
    });
}

// 删除下拉框所选项
function removeSelectedOption(value) {
    const optionToDelete = document.querySelector(`#id_sn option[value='${value}']`);
    optionToDelete.remove();
}

function get_sn_list_by_all_type(arg, type) {
    let sn_list = []
    $.ajax({
        type: 'POST',
        url: '/CMS/get_sn_list_by_all_type/',
        async: false,
        data: {
            arg: arg,
            type: type,
        },
        success: function (reply) {
            if (reply.type === 'success') {
                sn_list = reply.data['sn_list']
            } else {
                myAlert(reply.msg, reply.type)
            }
        }
    })
    return sn_list
}

function get_all_consumable_list() {
    let consumable_list = []
    $.ajax({
        type: 'POST',
        url: '/CMS/get_all_consumable_list/',
        async: false,
        success: function (reply) {
            if (reply.type === 'success') {
                consumable_list = reply.data['consumable_list']
            } else {
                myAlert(reply.msg, reply.type)
            }
        }
    })
    return consumable_list
}

/**
 * 下拉框新增选项
 * @param {*} select_id 下拉框ID
 * @param {*} data_list 下拉框所需數據 格式['123','456']
 * @param {*} empty 清空舊數據
 **/
function options_to_select(select_id, data_list, empty = true) {
    const id = '#' + select_id;

    if (empty) {
        $(id).empty().append('<option selected value=""></option>');
    }

    const res_list = [];
    let res_dict;
    for (let i = 0; i < data_list.length; i++) {
        res_dict = {}
        res_dict['id'] = data_list[i]
        res_dict['text'] = data_list[i]
        res_list.push(res_dict)
    }
    $(id).select2({
        // language: 'zh-hans',
        width: '80%',
        placeholder: '',
        // 最多字元限制
        maximumInputLength: 10,
        // 最少字元才觸發尋找, 0 不指定
        minimumInputLength: 0,
        // 當找不到可以使用輸入的文字
        tags: false,
        data: res_list,
        language: {
            noResults: function () {
                return "没有匹配结果";
            },
            searching: function () {
                return "正在搜索...";
            },
        }
    })
}


// 更新下拉框选项
function change_options(select_id, dataList) {
    // 获取下拉框元素
    let selectElement = document.getElementById(select_id);
    // 清除所有选项
    while (selectElement.firstChild) {
        selectElement.removeChild(selectElement.firstChild);
    }
    // 添加默认选项
    let defaultOptionElement = document.createElement('option');
    defaultOptionElement.value = 'all';
    defaultOptionElement.text = '全部';
    selectElement.appendChild(defaultOptionElement);
    // 添加新选项
    for (let i = 0; i < dataList.length; i++) {
        let optionElement = document.createElement('option');
        optionElement.value = dataList[i];
        optionElement.text = dataList[i];
        selectElement.appendChild(optionElement);
    }
    selectElement.value = 'all';
}


function get_ConsumableList_by_ConsumableType(ConsumableType) {
    let ConsumableList = []
    $.ajax({
        type: 'POST',
        url: '/CMS/get_ConsumableList_by_ConsumableType/',
        async: false,
        data: {
            ConsumableType: ConsumableType,
        },
        success: function (reply) {
            if (reply.type === 'success') {
                ConsumableList = reply.data['ConsumableList']
            } else {
                myAlert(reply.msg, reply.type)
            }
        }
    })
    return ConsumableList
}


function get_ConsumableList_by_Other(ConsumableType, ToolType, Version, Model, Status) {
    let ConsumableList = []
    $.ajax({
        type: 'POST',
        url: '/CMS/get_ConsumableList_by_Other/',
        async: false,
        data: {
            ConsumableType: ConsumableType,
            ToolType: ToolType,
            Version: Version,
            Model: Model,
            Status: Status,
        },
        success: function (reply) {
            if (reply.type === 'success') {
                ConsumableList = reply.data['ConsumableList']
            } else {
                myAlert(reply.msg, reply.type)
            }
        }
    })
    return ConsumableList
}


function createTable(headList, dataList) {
    // 创建表格元素
    var table = document.createElement('table');
    table.classList.add('table', 'table-striped', 'table-bordered');

    // 创建表头行
    var headRow = document.createElement('tr');
    for (var i = 0; i < headList.length; i++) {
        var headCell = document.createElement('th');
        headCell.textContent = headList[i];
        headRow.appendChild(headCell);
    }
    table.appendChild(headRow);

    var dataTable = $(table).DataTable(dt);

    for (var j = 0; j < dataList.length; j++) {
        dataTable.row.add(dataList[j]);
    }

    dataTable.draw();

    // 将表格添加到页面中
    document.body.appendChild(table);
}

// 批量获取modal模态框中的tbody数据
function getModalFormData(tableId) {
    var table = document.getElementById(tableId);
    var tbody = table.getElementsByTagName('tbody')[0];
    var rows = tbody.getElementsByTagName('tr');
    var data = [];

    for (var i = 0; i < rows.length; i++) {
        var row = rows[i];
        var inputs = row.getElementsByTagName('input');
        var rowData = [];
        for (var j = 0; j < inputs.length; j++) {
            rowData.push(inputs[j].value);
        }
        data.push(rowData);
    }

    return data;
}

function get_sn_list_by_mul_condition(sn = '', tooltype = 'all', version = 'all', status = 'all', model = 'all', ConsumableType = 'all') {
    let sn_list = []
    $.ajax({
        type: 'POST',
        url: '/CMS/get_sn_list_by_mul_condition/',
        async: false,
        data: {
            sn: sn,
            tooltype: tooltype,
            version: version,
            status: status,
            model: model,
            ConsumableType: ConsumableType,
        },
        success: function (reply) {
            if (reply.type === 'success') {
                sn_list = reply.data['sn_list']
            } else {
                myAlert(reply.msg, reply.type)
            }
        }
    })
    return sn_list
}