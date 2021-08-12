// pos_cash_in_out_odoo js
// console.log("custom callleddddddddddddddddddddd");
odoo.define('odoo_website_product_quote.web', function(require) {
	"use strict";
	var core = require('web.core');
	var QWeb = core.qweb;
	var _t = core._t;
	var sAnimations = require('website.content.snippets.animation');
	var rpc = require('web.rpc');
	var ajax = require('web.ajax');
	var session = require('web.session');
	var Widget = require('web.Widget');


	sAnimations.registry.websiteQuote=sAnimations.Class.extend({
		 selector: '.oe_website_sale',
		read_events: {    
			'change #txt': '_onClickQuote',
			'click #bt_non':'_onNonlogin',
			// 'change #country_id': '_onChangeCountry',
		},
		_onClickQuote: function () {
				var jsonObj = [];
				$('#tbl tbody tr').each(function(){
					var in_val = $(this).find("#txt > input[type=text]").val();
					var x = $(this).find('#txt').attr('line_id');
					// console.log("qtyyyyyyyyyyyyyyyyyyyyyy",in_val,x)
					var item = {}
					item [x] = in_val;
					jsonObj.push(item);	
					
				});
				var user = session.uid
				// console.log(session,"json1111111111111111111111111",user,this)
				this._rpc({
					route: "/quote/cart/update_json",
					params: {
						jsdata: jsonObj,
					},
				}).then(function (data) {
					window.location.href = '/quote/cart';
					// console.log("sdg11111111111111111111111111111111111111111",data)
				});
				// console.log("qwertyui===================================")
		},
		_onNonlogin: function () {
			var id1 = document.getElementById("txt1").value
			var obj = document.getElementById("obj").value
			// console.log(obj,"iddddddddddddddddddddddddd",id1)
			ajax.jsonRpc("/shop/product/quote/confirm/nonlogin","call",{
				'id1' : id1,
				'obj':obj,
			}).then(function (data) {
				window.location.href = '/thank_you';
			// console.log("sdg11111111111111111111111111111111111111111",data)
			});
		}
		// _onChangeCountry: function () {
		// 	if ($('.o_portal_details').length) {
		// 	var state_options = $("select[name='state_id']:enabled option:not(:first)");
		// 	var select = $("select[name='state_id']");
		// 	state_options.detach();
		// 	var displayed_state = state_options.filter("[data-country_id="+($(this).val() || 0)+"]");
		// 	var nb = displayed_state.appendTo(select).show().size();
		// 	select.parent().toggle(nb>=1);
			
		// 	$('.o_portal_details').find("select[name='country_id']").change();
		// 	}	
		// }
	});

	$(document).ready(function (){
	
	 if ($('.o_portal_details').length) {
		var state_options = $("select[name='state_id']:enabled option:not(:first)");
		$('.o_portal_details').on('change', "select[name='country_id']", function () {
			var select = $("select[name='state_id']");
			state_options.detach();
			var displayed_state = state_options.filter("[data-country_id="+($(this).val() || 0)+"]");
			var nb = displayed_state.appendTo(select).show();
			select.parent().toggle(nb>=1);
		});
		$('.o_portal_details').find("select[name='country_id']").change();
	}	
	
	
	// $("#btn_cart").click(function(ev){
	// 	var jsonObj = [];
	// 	$('#tbl tbody tr').each(function(){
	// 		var in_val = $(this).find("#txt > input[type=text]").val();
	// 		var x = $(this).find('#txt').attr('line_id');
	// 		// console.log("qtyyyyyyyyyyyyyyyyyyyyyy",in_val,x)
	// 		var item = {}
	// 		item [x] = in_val;
	// 		jsonObj.push(item);	
			
	// 	});
	// 	var user = session.uid
	// 	console.log(session,"json1111111111111111111111111",user,this)
	// 	// this._rpc({
	// 	rpc.query({
	// 		model: 'website',
	// 		method: 'get_qoute_cart_lines',
	// 		args: [1,jsonObj],
	// 	}).then(function (data) {
	// 		console.log("sdg11111111111111111111111111111111111111111",data)
	// 	});
	// 	console.log("qwertyui===================================")

	// });

	// $("#bt_non").click(function(ev){
	// 		var id1 = document.getElementById("txt1").value
	// 		// console.log("iddddddddddddddddddddddddd",id1)
	// 		ajax.jsonRpc("/shop/product/quote/confirm/nonlogin","call",{
	// 			'id1' : id1,
	// 		}).then(function (data) {
	// 			window.location.href = '/thank_you';
	// 		// console.log("sdg11111111111111111111111111111111111111111",data)
	// 		});
	// });
	

	});
});
