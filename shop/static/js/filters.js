var filterCache, filterChosen, tabPage, $filterForm;
var filterUrl = '/reports/load_filter/';

function normalizeAjaxDataList(dataList){
	for(i in dataList){
		var j = dataList[i];
		if(!j.name) j.name = '(empty)';
		if(typeof j != 'object') dataList[i] = {id: j, name: j};
	}
	return dataList;
}

function choosePage(page, tabIndex){
	tabPage = page;
	var cache = filterCache[tabIndex];

	var fillPage = function(){
		var $sel = $filterForm.children('.listview').empty();
		for each(i in cache[page])
			if(!filterChosen[tabIndex][i.id])
				$('<option>').val(i.id).text(i.name).draggable().appendTo($sel);
	}

	if(!cache[page] || !cache[page].length) $.getJSON(
		filterUrl,
		{
			f: tables[tabIndex],
			page: page
		},
		function(data){
			cache[page] = normalizeAjaxDataList(data.list);
			fillPage();
		}
	);
	else fillPage();
	
	return false;
}

function chooseFilterItem(tabIndex){
	var view = $filterForm.find('.listview>:selected'),
		chosen = $filterForm.children('.chosen_list');
	view.detach().appendTo(chosen).each(function(){
		this.selected = false;
		filterChosen[tabIndex][this.value] = 1;
	})

}

function moveFilterItemBack(tabIndex){
	var chosen = $filterForm.find('.chosen_list>:selected').each(function(){
		filterChosen[tabIndex][this.value] = 0;
	}).remove();
	choosePage(tabPage, tabIndex);
}

function initTab(index){
	var v = tables[index], id = 'filter_tabs' + index;

	var params = '(' + index + ')';
	var choose = 'chooseFilterItem' + params, undo = 'moveFilterItemBack' + params;

	$filterForm.empty().
		append($('<select multiple>').addClass('listview').droppable()).
		append($('<span class = "swappers">').
			append($('<button type = "button" class = "swapper1">').text('->').attr('onclick', choose)).
			append($('<button type = "button" class = "swapper2">').text('<-').attr('onclick', undo))
		).
		append($('<select multiple>').
			addClass('chosen_list').
			attr('name', 'filter_' + v).
			droppable()).
		append($('<div class = "filter_except">').
			append($('<label>').
				append($('<input type = "radio" value = "1" class = "exclude">').
					attr('name', 'exclude_' + v)).
				append('exclude')
			).
			append($('<label>').
				append($('<input type = "radio" value = "0" class = "filter">').
					attr('name', 'exclude_' + v)).
				append('filter')
			)
		);

	$.getJSON(
		filterUrl,
		{
			f: tables[index]
		},
		function(data){
			var $d = $('#filter_page' + index);
			if(data.page_count > 1) for(var i = 0; i < data.page_count; i++){
				var func = 'return choosePage(' + i + ', ' + index + ')';
				$('<a href = "#">').attr('onclick', func).text(i+1).appendTo($d);
			}
			filterCache[index] = new Array(data.page_count);
			filterCache[index][0] = normalizeAjaxDataList(data.list);
			var $sel = $filterForm.find('.chosen_list')
			for each(i in data.saved){
				$sel.append($('<option>').val(i.id).text(i.name));
				filterChosen[index][i.id] = 1;
			}
			$filterForm.find('input.' + (data.exclude? 'exclude':'filter')).attr('checked', 'checked');
			choosePage(0, index);
		}
	);

}

$(function(){
	filterCache = new Array(tables.length);
	filterChosen = new Array(tables.length);
	var $ul = $('#filter_list');
	var $f = $('#filters');
	for(i in tables){
		filterCache[i] = [];
		filterChosen[i] = {};
		var h = '#filter_tabs' + i;
		$('<li>').append(
			$('<a>').attr('href', h).text(tables[i])
		).appendTo($ul);
		var id = 'filter_tabs' + i;

		var $divid = function(id){return $('<div>').attr('id', id);}

		var $d = $divid(id);
		$d.appendTo($f);
		$d.append($divid('filter_page' + i).addClass('filter_page'));
		$d.append(
			$divid('filter_form' + i).addClass('filter_form')
		).
		append($('<button name = "save" type = "button">save</button>').click(saveClick));
	}
	var onselect = function(event, ui){
		var index = ui.index, $panel = $(ui.panel);
		$filterForm = $('#filter_form' + index);
		if(!filterCache[index].length) initTab(index);
	}
	$('#filters').tabs({
		selected: -1,
		select: onselect
	}).tabs({selected: 0});
});

var setSel = function(sel){
	return function(){
		this.selected = sel;
	}
}

function saveClick(){
	var $chosenOptions = $('#filters .chosen_list option');
	$chosenOptions.each(setSel(true));
	var data = $('#filters').serializeArray();
	$chosenOptions.each(setSel(false));
	
	data.push({
		name: 'save'
	})
	$.post(filterUrl, data, function(rec){

	});
}