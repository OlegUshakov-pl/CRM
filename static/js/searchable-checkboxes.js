function filterCheckboxes(input) {
    var query = input.value.toLowerCase();
    var container = input.closest('.searchable-checkbox-group');
    var labels = container.querySelectorAll('.checkbox-container label');
    labels.forEach(function(label) {
        var text = label.textContent.toLowerCase();
        label.style.display = text.indexOf(query) > -1 ? '' : 'none';
    });
}
