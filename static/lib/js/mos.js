//ComboBox
;(function ($) {
	$.fn.extend({
		"MoSList" : function(opts){
			var def = {
				caption : '',
				items : [],
				selectedIndex : -1
			};
			var option = $.extend({}, def, opts);
			
			this.each(function(){ //用each处理选择器选中的一个或多个dom节点
                var $this = $(this);
                $this.addClass("dropdown");
                var html = [];
                html.push("<span>" + option.caption + "</span>");
                html.push("<ul class='dropdown-select'>");
                for(var i = 0; i < option.items.length; i++){
                	html.push("<li>" + option.items[i] + "</li>");
                }
                html.push("</ul>");
                $this.append(html.join(''));
            
        	$this.on("click", function(){
        			var h = $this.height();
        			$this.find("ul").css({"display":"block","top": h});
	        	})
                
            $this.find("li").on("click", function(){
            			$this.find("span").html(this.innerText);
        				$this.find("ul").css("display", "none");
        				return false;
	            	})
            });
            
            return this; //返回被选中的元素节点，以供后续操作。
		}
	});
})(jQuery);