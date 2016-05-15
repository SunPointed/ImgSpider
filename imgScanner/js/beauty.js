$(initPage);

function initPage(){

	var debug = true;

	var urlList = [],
		index = 0,
		stepLength = 5,
		data,
		isConnect = false,
		defaultUrl = "",
		url,
		key;
		scrollPosition = 0;
		
	var $show_area = $('#show_area'),
		$key = $('#key'),
		$address = $('#address'),
		$btn_start = $('#btn_start'),
		$btn_stop = $('#btn_stop'),
		$big_show = $('#big_show'),
		$show_area = $('#show_area'),
		$back = $('#back'),
		$img_show = $('#img_show'),
		$next = $('#next'),
		$exit = $('#exit');

	// 设置服务器的端口
	var socket = new WebSocket('ws://localhost:8080/');		

	/*
	 *	html action
	 */
	$btn_start.on('click',function () {
		if(isConnect){
			url = $address.val();
			key = $key.val();
			if(url.length === 0){
				url = defaultUrl;
			}
			if(key.length === 0){
				key = defaultUrl;
			}
			socket.send('{"type":"start","args":["'+ url +'","'+ key +'"]}');
		}
	});

	$btn_stop.on('click',function () {
		if(isConnect){
			socket.send('{"type":"stop","args":[]}');
		}
	});

	$exit.on('click', function () {
		$show_area.css('visibility','visible');
		$big_show.css('visibility','hidden');
	});

	/*
	 *	socket 
	 */
	socket.onmessage = function(evt){
		data = JSON.parse(evt.data);
			
		if(data.type === 'start'){

		} else if(data.type === 'stop'){

		} else if(data.type === 'imgs'){
			for(var i=0; i<data.args.length; i++){
				urlList.push(data.args[i]);
				addPicture($show_area, data.args[i], urlList.length-1, urlList);
			}
			index += stepLength;
		}
	};

	socket.onclose = function(evt){

	};

	socket.onerror = function(evt) { 

    };

    socket.onopen = function(evt){
    	log(debug, "open");
    	isConnect = true;
	};
}

function addPicture(area, url, index, urlList){
	var http = url.substring(0,4);
	if(http !== 'http'){
		urlList.pop();
		return;
	}
	area.append('<div class="Picture" id="picture_'+ index +'"><img src="'+ url +'" alt="xxx"></div>');
	$('#picture_'+index).on('click', function (){
		var $big_show = $('#big_show'),
			$show_area = $('#show_area'),
			$back = $('#back'),
			$img_show = $('#img_show'),
			$next = $('#next'),
			$exit = $('#exit');

		var url,
			id,
			data;

		$show_area.css('visibility','hidden');
		$big_show.css('visibility','visible');	
		
		url = $(this).children('img').attr('src');
		id = $(this).attr('id');
		data = id.split('_');
		// data = ['sd','5'];

		$img_show.children().remove();
		$img_show.append('<img src="'+ url +'">');

		$back.on('click', function () {
			if(data[1] != 0){
				data[1]--;
				id = data[0] + '_' + data[1];
				url = $('#'+id).children('img').attr('src');

				$img_show.children().remove();
				$img_show.append('<img src="'+ url +'">');
			} else {
				alert('已经是第一张！');
			}
		});

		$next.on('click', function () {
			if(data[1] != urlList.length-1){
				data[1]++;
				id = data[0] + '_' + data[1];
				url = $('#'+id).children('img').attr('src');

				$img_show.children().remove();
				$img_show.append('<img src="'+ url +'">');
			} else {
				alert('已经是最后一张！');
			}
			// if(data[1] != 10){
			// 	data[1]++;
			// 	alert(data[1]);
			// }
		});
	});
}

function log(debug, text){
	if(debug){
		console.log(text);
	}
}








