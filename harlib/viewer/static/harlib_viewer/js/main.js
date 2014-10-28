$(function(){

    String.prototype.trim = function(){return this.replace(/^\s+|\s+$/g, '');};

    window.gHarFile = {};

    Handlebars.registerHelper('list', function(items, options) {
        var out = ''
        if (!items) {
            return out;
        }
        for(var i = 0, l = items.length; i < l; i++) {
            out += options.fn(items[i]);
        }
        return out;
    });

    var headersTemplate = Handlebars.compile($('#headers-template').html());

    Handlebars.registerHelper('headers', function(items, options) {
        return headersTemplate(items);
    });

    var headersTabTemplate = Handlebars.compile($('#headers-tab-template').html());

    var cookiesTemplate = Handlebars.compile($('#cookies-template').html());

    Handlebars.registerHelper('cookies', function(cookies, options) {
        return cookiesTemplate(cookies);
    });

    var cookiesTabTemplate = Handlebars.compile($('#cookies-tab-template').html());

    var paramsTemplate = Handlebars.compile($('#params-template').html());

    Handlebars.registerHelper('params', function(items, options) {
        return paramsTemplate(items);
    });

    var paramsTabTemplate = Handlebars.compile($('#params-tab-template').html());

    var postDataTabTemplate = Handlebars.compile($('#postdata-tab-template').html());

    var responseTabTemplate = Handlebars.compile($('#response-tab-template').html());

    Handlebars.registerHelper('times', function(obj, options) {
        var out = ''
        if (!obj) {
            return out;
        }
        for(i in obj) {
            if (obj.hasOwnProperty(i)) {
                out += options.fn({"name": i, "value": obj[i]});
            }
        }
        return out;
    });

    var timingsTemplate = Handlebars.compile($('#timings-template').html());

    Handlebars.registerHelper('timings', function(items, options) {
        return timingsTemplate(items);
    });

    var timingsTabTemplate = Handlebars.compile($('#timings-tab-template').html());

    var socketOptionsTabTemplate = Handlebars.compile($('#socket-options-template').html());

    Handlebars.registerHelper('sockopts', function(items, options) {
        return socketOptionsTabTemplate(items);
    });

    var optionsTabTemplate = Handlebars.compile($('#options-tab-template').html());


    var entryTemplate = Handlebars.compile($('#entry-template').html());

    Handlebars.registerHelper('entry', function(entry, options) {
        return entryTemplate(entry);
    });

    Handlebars.registerHelper('entries', function(entries, options) {
        var out = ''
        if (!entries) {
            return out;
        }
        for(var i = 0, l = entries.length; i < l; i++) {
            entry = entries[i];
            entry._index = i;
            out += entryTemplate(entry)
        }
        return out;
    });

    var entriesListTemplate = Handlebars.compile($('#entries-list-template').html());

    window.hasHeaders = function (message) {
        if (!message) return false;
        if (!message.headers) return false;
        if (!message.headers.length) return false;
        return true;
    };

    window.hasCookies = function (message) {
        if (!message) return false;
        if (!message.cookies) return false;
        if (!message.cookies.length) return false;
        return true;
    };

    window.hasParams = function (entry) {
        if (!entry) return false;
        if (!entry.request) return false;
        if (!entry.request.queryString) return false;
        if (!entry.request.queryString.length) return false;
        return true;
    };

    window.hasPostData = function (entry) {
        if (!entry) return false;
        if (!entry.request) return false;
        if (!entry.request.postData) return false;
        if (!entry.request.postData.params) return false;
        if (!entry.request.postData.params.length) return false;
        return true;
    };

    window.hasContent = function (entry) {
        if (!entry) return false;
        if (!entry.response) return false;
        if (!entry.response.content) return false;
        if (!entry.response.content.size) return false;
        return true;
    };

    window.hasSocketOptions = function (entry) {
        if (!entry) return false;
        if (!entry._socketOptions) return false;
        if (!entry._socketOptions.length) return false;
        return true;
    };

    window.onInputHarFile = function (file) {
        var log = file.log;
        if (!log) {
            if (file.startedDateTime) {
                log = {"version": "1.2", "entries": [file]};
            }
        }
        $('#entries')	.html(entriesListTemplate(log));

        var $list = $('#entries > table > tbody > tr');
        var tag = $list[0].children[1].children[0];
        window.onClickHarEntry(tag);
        return;
    };

    window.onInputHarEntry = function (entry) {
        $('#headers')	.html(headersTabTemplate(entry));
        $('#cookies')	.html(cookiesTabTemplate(entry));
        $('#params')	.html(paramsTabTemplate(entry));
        $('#postData')	.html(postDataTabTemplate(entry));
        $('#response')	.html(responseTabTemplate(entry));
        $('#timing')	.html(timingsTabTemplate(entry));
        $('#options')	.html(optionsTabTemplate(entry));

        $('.main-panel .tab-pane').each(function(index, value){
            var $value = $(value);
            var $valueTab = $('#' + value.id + '-tab');
            $valueTab.addClass('hidden');
            if ($value.html().trim()) {
                $valueTab.removeClass('hidden');
            }
        });

        if (!(hasCookies(entry.request) | hasCookies(entry.response))) {
            $('#cookies-tab').addClass('hidden');
        }

        if (!(hasParams(entry))) {
            $('#params-tab').addClass('hidden');
        }

        if (!(hasPostData(entry))) {
            $('#postData-tab').addClass('hidden');
        }

        if (!(hasContent(entry))) {
            $('#response-tab').addClass('hidden');
        }

        if (!(hasSocketOptions(entry))) {
            $('#options-tab').addClass('hidden');
        }

        return;
    };

    window.onClickHarEntry = function (tag) {
        var index = $(tag).data('index');
        var $list = $('#entries > table > tbody > tr');
        $list.each(function(index, value){
            $(value).removeClass('info');
        });
        $($list[index]).addClass('info');

        var entry = window.gHarFile.log.entries[index];
        window.onInputHarEntry(entry);
        return;
    };

    window.onClickRemoteOpen = function (tag, event) {
    };

    window.onClickLocalOpen = function (tag, event) {
        var $tag = $('#local-file')[0];
        var reader = new FileReader();
        reader.onload = function(event) {
            var text = event.target.result
            window.gHarFile = JSON.parse(text);
            window.onInputHarFile(window.gHarFile);
        };
        reader.readAsText($tag.files[0]);
    };

    window.onClickDirectOpen = function (tag, event) {
        var $tag = $('#direct-input-data')[0];
        window.gHarFile = JSON.parse($tag.value);
        window.onInputHarFile(window.gHarFile);
    };

    //window.onInputHarFile(gHarFile);
});
