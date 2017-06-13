/**
 * Created by gufy on 16/12/20.
 */

//JS For edit host info
function EditHostInfo(url) {
    $.getJSON(url, function(data) {
        $('#editusername').val(data.username);
        $('#editpassword').val(data.password);
        $('#editip').val(data.ip);
        $('#edithostname').val(data.hostname);
        $('#editHostInfoFormModal').modal();
    });
}

