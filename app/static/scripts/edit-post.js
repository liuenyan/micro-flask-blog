categoriesSelect = document.getElementById('categories');

$('.btn-add-category').on('click', function(e){
    //submit category
    newCategory = document.getElementById('new-category');
    if(newCategory.value.length != 0){
        $.ajax({
            type: "POST",
            url: "/add-category",
            data: {"new_category": newCategory.value},
            dataType: "json"
        }).done(function(jsonData){
            if(jsonData['result'] == "true"){
                //修改select
                newOption = document.createElement('option');
                newOption.value = jsonData['category_id'];
                newOption.appendChild(document.createTextNode(jsonData['category_name']));
                categoriesSelect.appendChild(newOption);
                categoriesSelect.value = jsonData['category_id'];
                $('#modal-add-category').modal('toggle');
                
            }else{
                alert("添加分类失败");
            }
        });
    }
});
