onDragEnter = function (event) {
    event.preventDefault();
},

onDragOver = function (event) {
    event.preventDefault();
},

onDragLeave = function (event) {
    event.preventDefault();
},

onDrop = function (event, a) {
    event.preventDefault();
    var inputId = $(event.target).data('target');
    var input = document.getElementById(inputId);
    var inputName = input.name
    var fileName = event.originalEvent.dataTransfer.files[0].name;
    var file = event.originalEvent.dataTransfer.files;

    $('#file-name-termo_posse').html(fileName);
    $(`#footer-${inputName}`).hide()

    input.files = event.originalEvent.dataTransfer.files;
};

$('input[type="file"]').each((key, element) => {
    $(`#${element.id}`).on("change", function (event) {
        var inputName = event.target.name;
        var newFile = event.target.files[0];
        $(`#file-name-${inputName}`).html(newFile.name);
        $(`#footer-${inputName}`).hide();
    });

    $(`#drag-space-${element.name}`)
        .on("dragenter", onDragEnter)
        .on("dragover", onDragOver)
        .on("dragleave", onDragLeave)
        .on("drop", onDrop)
        .on("click", () => {
            $(`#${element.id}`).trigger('click');
        });
});