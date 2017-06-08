var data = source.data;
var filetext = 'group_name,group_user_name,content,createdAt\n';
for (i=0; i < data['group_name'].length; i++) {
    var currRow = [data['group_name'][i].toString(),
                   data['group_user_name'][i].toString(),
                   data['content'][i].toString(),
                   //data['user_img'][i].toString(),
                   data['createdAt'][i].toString().concat('\n')];
    var joined = currRow.join();
    filetext = filetext.concat(joined);
}

var filename = 'data_result.csv';
var blob = new Blob([filetext], { type: 'text/csv;charset=utf-8;' });

//addresses IE
if (navigator.msSaveBlob) {
    navigator.msSaveBlob(blob, filename);
}

else {
    var link = document.createElement("a");
    link = document.createElement('a')
    link.href = URL.createObjectURL(blob);
    link.download = filename
    link.target = "_blank";
    link.style.visibility = 'hidden';
    link.dispatchEvent(new MouseEvent('click'))
}
