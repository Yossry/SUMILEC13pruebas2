odoo.define('module.DianInvoice', function(require) {
    "use strict";
    var rpc = require('web.rpc');
    var loaded = false;
    $(document).ready(function() 
    {
        var flagLoaded = false;
        var mainIntervalTime = 2500;
        var itv = setInterval(function() 
        {
            if($("form.checkout_autoformat").length>0)
            {   
                $(".div_zip").remove()
                var country_id = $('#country_id option:contains(Colombia)').val();
                $("#country_id").val(country_id);
                

                init_xcity_selection()             

                $(document).on("blur", "input[name='vat_num']", function()
                {
                    update_nit_cod_verification();
                });
                $(document).on("blur", "input[name='firstname']", function()
                {
                    update_customer_full_name();
                });
                $(document).on("blur", "input[name='other_name']", function()
                {
                    update_customer_full_name();
                });
                $(document).on("blur", "input[name='lastname']", function()
                {
                    update_customer_full_name();
                });
                $(document).on("blur", "input[name='other_lastname']", function()
                {
                    update_customer_full_name();
                }); 

                $(document).on("change", "select[name='state_id']", function() 
                {
                    populate_xcity_field(false);
                });
                $(document).on("change", "select[name='company_type']", function()
                {
                    onchange_company_type();
                });
                $(document).on("change", "select[name='l10n_co_document_type']", function()
                {
                    onchange_document_type();
                });
                $(document).on("change", "select[name='city_id']", function()
                {
                    var xcity_zip = $(this).find('option:selected').attr('code');
                    var xcity_name = $(this).find('option:selected').text();
                    $("input[name='zip']").val(xcity_zip);
                    $('input[name="city"]').val(xcity_name);
                }); 

                clearInterval(itv)

            }
        
        function init_xcity_selection() 
        {
            
            populate_states(country_id);
            if($("select[name='city_id']").find('option').length == 0)
            {                
                populate_xcity_field(true);
            }
        }

        function update_nit_cod_verification()
        {
            var doc_type = $("select[name='l10n_co_document_type']").val()
            var doc_num  = $("input[name='vat_num']").val()
            if(doc_type=="rut")
            {
                var doc_num_code = dian_nit_codigo_verificacion(doc_num);
                $("input[name='vat_vd']").val(doc_num_code);
            }
            
        }
        function set_document_type()
        {
            var company_name = $("input[name='company_name']").val(); 
            if(String(company_name)=="")
            {
                $("select[name='l10n_co_document_type']").val("id_document");
                $("input[name='vat_vd']").val('');
            }
            if(String(company_name).length > 0 )
            {
                $("select[name='l10n_co_document_type']").val("rut");
            }
        }
        function update_customer_full_name()
        {
             var first_name_1 = $("input[name='firstname']").val();
            var first_name_2 = $("input[name='other_name']").val();
            var last_name_1 = $("input[name='lastname']").val();
            var last_name_2 = $("input[name='other_lastname']").val();
            var full_name = String(first_name_1) + String(" ") + String(first_name_2) + String(" ") + String(last_name_1) + String(" ") + String(last_name_2);
            $("input[name='name']").val(full_name);

        }

        function onchange_document_type()
        {
            var document_type =  $("select[name='l10n_co_document_type']").val()
            if (document_type == 'rut'){
                $("select[name='vat_type']").val("31");
                $("input[name='is_company']").prop( "checked", true );}
            else if (document_type == 'id_document'){
                $("select[name='vat_type']").val("13");
                 $("input[name='is_company']").prop( "checked", false );}
            else if (document_type == 'id_card'){
                $("select[name='vat_type']").val("12");
                 $("input[name='is_company']").prop( "checked", false );}
            else if (document_type == 'passport') {
                $("select[name='vat_type']").val("41");
                 $("input[name='is_company']").prop( "checked", false );}
            else if (document_type == 'foreign_id_card'){
                $("select[name='vat_type']").val("22");
                 $("input[name='is_company']").prop( "checked", false );}
            else if (document_type == 'external_id'){
                $("select[name='vat_type']").val("");
                 $("input[name='is_company']").prop( "checked", false );}
            else if (document_type == 'diplomatic_card'){
                $("select[name='vat_type']").val("");
                 $("input[name='is_company']").prop( "checked", false );}
            else if (document_type == 'residence_document'){
                $("select[name='vat_type']").val("");
                 $("input[name='is_company']").prop( "checked", false );}
            else if (document_type == 'civil_registration'){
                $("select[name='vat_type']").val("11");
                 $("input[name='is_company']").prop( "checked", false );}
            else if (document_type == 'national_citizen_id'){
                $("select[name='vat_type']").val("13");
                 $("input[name='is_company']").prop( "checked", false );}
        }

        function onchange_company_type()
        {
            var company_type_val =  $("select[name='company_type']").val()
            if (company_type_val == "person"){
                $("input[name='firstname']").show();
                $("input[name='other_name']").show();
                $("input[name='lastname']").show();
                $("input[name='other_lastname']").show();
                $("input[name='firstname']").val("");
                $("input[name='other_name']").val("");
                $("input[name='lastname']").val("");
                $("input[name='other_lastname']").val("");
                $("input[name='name']").hide();
                $("select[name='l10n_co_document_type']").val("id_document");
                $("input[name='is_company']").prop( "checked", false );
            }else{
                $("input[name='firstname']").hide();
                $("input[name='other_name']").hide();
                $("input[name='lastname']").hide();
                $("input[name='other_lastname']").hide();
                $("input[name='name']").show();
                $("input[name='name']").val("");
                $("select[name='l10n_co_document_type']").val("rut");
                $("input[name='is_company']").prop( "checked", true );
            }
            onchange_document_type();

        }

        function populate_xcity_field(set_partner_city=false)
        {
            var state_id = $("select[name='state_id']").val();

            var data = { "params": { "state_id": state_id } }
            
                $.ajax({
                    type: "POST",
                    url: '/l10n_co_res_partner/get_state_city/',
                    data: JSON.stringify(data),
                    dataType: 'json',
                    contentType: "application/json",
                    async: false,
                    success: function(response) 
                    {
                        if (response.result.state_cities) 
                        {

                            try {
                                    var xcities_options = String();

                                    var xcities = response.result.state_cities;

                                    xcities_options = "<option value=''>Ciudad...</option>";
                                    xcities.forEach(function (xcitie, index) 
                                    {
                                        xcities_options = String(xcities_options) + "<option value='" + String(xcitie.id) + "' code='" + String(xcitie.code) + "'>" + String(xcitie.name) + "</option>";
                                        //console.log(xcities_options)
                                    });  
                                    
                                    $("select[name='city_id']").html('');
                                    $("select[name='city_id']").append(xcities_options);
                                    var code = $("select[name='city_id'] option:selected").attr("code")
                                    $("input[name='zip']").val(code) 
                                    if(set_partner_city)
                                    {
                                        

                                        var partner_id = $("input[name='partner_id']").val();
                                        var data = { "params": { "partner_id": partner_id } }

                                        $.ajax
                                        ({
                                            type: "POST",
                                            url: '/l10n_co_res_partner/get_partner_state_city/',
                                            data: JSON.stringify(data),
                                            dataType: 'json',
                                            contentType: "application/json",
                                            async: false,
                                            success: function(response) 
                                            {
                                                if (response.result.xcity_id_!=null) 
                                                {
                                                    $("select[name='city_id']").val(response.result.xcity_id_.city_id)
                                                    var code = $("select[name='city_id'] option:selected").attr("code")
                                                    $("input[name='zip']").val(code)  
                                                }
                                            }
                                        });
                                    }

                                }
                            catch (error) 
                            {console.log(error) }
                        }
            
                    }
                });

        }

        function populate_states(country_id)
        {
            var data = { "params": { "mode": "shipping" } }
            var country_id = $('#country_id option:contains(Colombia)').val();
                $.ajax({
                    type: "POST",
                    url: '/shop/country_infos/' + String(country_id),
                    data: JSON.stringify(data),
                    dataType: 'json',
                    contentType: "application/json",
                    async: false,
                    success: function(response) 
                    {
                        var xidentification = $('input[name="vat_num"]').val();
                        if(String(xidentification).length==0)
                        {

                        
                        if(response.result.states)
                        {
                            var states = response.result.states;
                            var options = "<option value=''>Departamento...</option>"
                            states.forEach(function(state,index)
                            {
                                // [679, "Vichada", "VID"]
                               if(parseInt(state[0])>0)
                                   options = options + String("<option value='"+state[0]+"' data-code='"+state[2]+"'>") + String(state[1]) +String("<option>")
                            });
                            $("select[name='state_id']").html("");
                            $("select[name='state_id']").append(options);
                            $("select[name='state_id'] option").not( "[value]" ).remove();
                            var xcity_code = $("select[name='city_id'] option:selected").attr("code");
                            var xcity_name = $("select[name='city_id'] option:selected").text();
                            $("input[name='zip']").val(xcity_code);
                            $('input[name="city"]').val(xcity_name);

                        }
                    }
                    }
                });

        }

        function dian_nit_codigo_verificacion(myNit) 
        {
            var vpri,
                x,
                y,
                z;
        
            // Se limpia el Nit
            myNit = myNit.replace(/\s/g, ""); // Espacios
            myNit = myNit.replace(/,/g, ""); // Comas
            myNit = myNit.replace(/\./g, ""); // Puntos
            myNit = myNit.replace(/-/g, ""); // Guiones
        
            // Se valida el nit
            if (isNaN(myNit)) {
                console.log("El nit/cédula '" + myNit + "' no es válido(a).");
                return "";
            };
        
            // Procedimiento
            vpri = new Array(16);
            z = myNit.length;
        
            vpri[1] = 3;
            vpri[2] = 7;
            vpri[3] = 13;
            vpri[4] = 17;
            vpri[5] = 19;
            vpri[6] = 23;
            vpri[7] = 29;
            vpri[8] = 37;
            vpri[9] = 41;
            vpri[10] = 43;
            vpri[11] = 47;
            vpri[12] = 53;
            vpri[13] = 59;
            vpri[14] = 67;
            vpri[15] = 71;
        
            x = 0;
            y = 0;
            for (var i = 0; i < z; i++) {
                y = (myNit.substr(i, 1));
                // console.log ( y + "x" + vpri[z-i] + ":" ) ;
        
                x += (y * vpri[z - i]);
                // console.log ( x ) ;    
            }
        
            y = x % 11;
            // console.log ( y ) ;
        
            return (y > 1) ? 11 - y : y;
        }
        
        },mainIntervalTime);
    });
});
    