function resetTable(){
	$(function () {
        $('.table-expandable').each(function () {
            var table = $(this);
            table.children('thead').children('tr').append('<th></th>');
            table.children('tbody').children('tr').filter(':odd').hide();
            table.children('tbody').children('tr').filter(':even').click(function () {
                var element = $(this);
                $(".selected").removeClass("selected");
                element.addClass("selected");
                element.next('tr').toggle('slow');
                element.find(".table-expandable-arrow").toggleClass("up");
            });
            table.children('tbody').children('tr').filter(':even').each(function () {
                var element = $(this);
                element.append('<td><div class="table-expandable-arrow"></div></td>');
            });
        });
    });
}

function setTableEditor(){
	$(".editor").off("click");
	$(".timepart-edit").on("click", function(){
		var $el = $(this);
		var val = $el.find(".cell-value").text();
		
		if ($el.find(".cell-value").css("display") != "none"){
			$el.find(".cell-value").css("display", "none");
			var html = [];
			html.push("<input class='table-editor' value='" + val + "'>");
			$el.append(html.join(''));
			
			$el.find("input").focus();
			$el.find("input").focusout(function(){
				val = $(this).val();
				$el.find(".cell-value").text(val);
				$el.find(".cell-value").css("display","block");
				$(this).remove();
			});
		}
	});
	$(".day-night").on("click", function(){
		var $el = $(this);
		var val = $el.find(".cell-value").text();
		
		if ($el.find(".cell-value").css("display") != "none"){
			$el.find(".cell-value").css("display", "none");
			var html = [];
			html.push("<select class='table-editor'>");
			html.push("<option value='Day'>Day</option>");
			html.push("<option value='Night'>Night</option>");
			html.push("</select>");
			$el.append(html.join(''));
			
			$el.find("select").val(val);
			$el.find("select").focus();
			$el.find("select").focusout(function(){
				val = $(this).val();
				$el.find(".cell-value").text(val);
				$el.find(".cell-value").css("display","block");
				$(this).remove();
			});
		}
	});
	$(".time-edit").on("click", function(){
		var $el = $(this);
		var val = $el.find(".cell-value").text();
		
		if ($el.find(".cell-value").css("display") != "none"){
			$el.find(".cell-value").css("display", "none");
			var html = [];
			html.push("<input class='timepicker' value='" + val + "'>");
			$el.append(html.join(''));
			$el.find("input.timepicker").timepicker({
				timeFormat:"HH:mm",
				change : function(tm){
					val = $(this).val();
					$el.find(".cell-value").text(val);
					$el.find(".cell-value").css("display","block");
				}
			});
			
			$el.find("input").focus();
			$el.find("input").focusout(function(){
				val = $(this).val();
				$el.find(".cell-value").text(val);
				$el.find(".cell-value").css("display","block");
				$(this).remove();
			});
		}
	})
}