


var additional_fields = ["id_plot_type", "id_house_type", "id_flat_type", "id_year_of_construction_from", "id_year_of_construction_to"];
hide_form_inputs(additional_fields);

$("#id_property_type").on('change', function(){
    if($("#id_property_type").val()=='plot'){
        hide_form_inputs(additional_fields);
        show_form_input("id_plot_type");
    }else if($("#id_property_type").val()=='house'){
        hide_form_inputs(additional_fields);
        show_form_inputs(["id_house_type", "id_year_of_construction_from", "id_year_of_construction_to"]);
    }else if($("#id_property_type").val()=='flat'){
        hide_form_inputs(additional_fields);
        show_form_inputs(["id_flat_type", "id_year_of_construction_from", "id_year_of_construction_to"]);
    }else if($("#id_property_type").val()=='garage'){
        hide_form_inputs(additional_fields);
        show_form_inputs(["id_year_of_construction_from", "id_year_of_construction_to"]);
    }else{
        hide_form_inputs(additional_fields);
    }
});

function hide_form_input(name){
    $(`label[for='${name}']`).hide();
    $(`#${name}`).hide();
}

function show_form_input(name){
    $(`label[for='${name}']`).show();
    $(`#${name}`).show();
}

function show_form_inputs(names){
    names.forEach(name => show_form_input(name));
}

function hide_form_inputs(names){
    names.forEach(name => hide_form_input(name));
}