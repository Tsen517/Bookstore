function showNewCategoryInput(selectElem) {
    var input = selectElem.parentNode.querySelector('.new-category-input');
    if (selectElem.value === 'add_new') {
        input.style.display = 'inline-block';
        input.required = true;
    } else {
        input.style.display = 'none';
        input.required = false;
    }
}