function filterSelectOptions(input) {
    var query = input.value.toLowerCase();
    var select = input.closest('.searchable-select-group').querySelector('select');
    for (var i = 0; i < select.options.length; i++) {
        var opt = select.options[i];
        opt.style.display = opt.text.toLowerCase().indexOf(query) > -1 ? '' : 'none';
    }
}
