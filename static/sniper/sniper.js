//sniper.js

function Sniper() {
  var $this = this;
  var handlers = {};
  var preHandleCallbacks = [];
  var postHandleCallbacks = [];

  this.construct = function() {
    this.registerHandler(new SniperJSLog());
    this.registerHandler(new SniperInsertTextHandler());
    this.registerHandler(new SniperRefreshHandler());
    this.registerHandler(new SniperRedirect());
    this.registerHandler(new SniperAlertDialogHandler());
    this.registerHandler(new SniperAppendTextHandler());
    this.registerHandler(new SniperSetCSSHandler());
    this.registerHandler(new SniperJSCallHandler());
    this.registerHandler(new SniperDeleteFromDOMHandler());
    this.registerHandler(new SniperPushStateHandler());

    $.ajaxSetup({
      success: function(data){
        $this.handleResponse(this.url, data);
      },
      async: false,
    });

    $(document).on(
      {
        click: function(event) {
          event.preventDefault();
          $this.request($(this).data('sniper'), {});
        }
      },
      'a[data-sniper]'
    );

    $(document).on(
      {
        submit: function(event) {
          event.preventDefault();
          $.ajax({
            url: $(this).attr('action'),
            type: $(this).attr('method'),
            data: $(this).serialize(),
          });
        }
      },
      'form[data-sniper]'
    );

   if (window.__sniper_onload) {
      this.handleResponse(null, window.__sniper_onload);
    }
  }

  this.registerHandler = function(sniper) {
    handlers[sniper.ident] = sniper;
  }

  this.registerPostHandleCallback = function(callback) {
    postHandleCallbacks.push(callback);
  }

  this.registerPreHandleCallback = function(callback) {
    preHandleCallbacks.push(callback);
  }

  this.request = function(url, data) {
    $.ajax({
      url: url,
      data: data,
    }); 
  }

  this.handleResponse = function(source, data) {
    if (data.__obj_ident !== '__sniper_transport' && data.__obj_ident !== '__sniper_onload') {
      throw new Error(source + " did not return a valid sniper response");
    }

    var snipers = data.__snipers.sort(function(a, b) {
      return a.__index - b.__index;
    });

    for (var i in preHandleCallbacks) {
      preHandleCallbacks[i]();
    }

    for (var index in snipers) {
      var cur_sniper = snipers[index];
      var cur_sniper_kwargs = cur_sniper['__sniper_kwargs'];
      var cur_sniper_ident = cur_sniper['__sniper_ident'];
      var handler = handlers[cur_sniper_ident];

      //unescape all strings
      for (var key in cur_sniper_kwargs) {
        if (cur_sniper_kwargs[key].substring) {
          var str = cur_sniper_kwargs[key]; 
          var decoded = $("<div />").html(str).text();
          cur_sniper_kwargs[key] = decoded;
        }
      }

      if (handler) {
        handler.handle(source, cur_sniper_kwargs);
      } else {
        throw new Error("No handler found for ident: " + cur_sniper_ident);
      }
    }

    for (var i in postHandleCallbacks) {
      postHandleCallbacks[i]();
    }
  }

  this.construct();
}

//handlers
function SniperJSLog() {
  this.ident = '__bi_js_log';
  this.handle = function(source, kwargs) {
    console.log.apply(console, kwargs.args);
  }
}

function SniperDeleteFromDOMHandler() {
  this.ident = '__bi_dom_delete';
  this.handle = function(souce, kwargs) {
    $(kwargs.dom_ident).remove();
  }
}

function SniperInsertTextHandler() {
  this.ident = '__bi_insert_text'; 
  this.handle = function(source, kwargs) {
    $(kwargs.dom_ident).html(kwargs.text);
  }
}

function SniperAppendTextHandler() {
  this.ident = '__bi_append_text';
  this.handle = function(source, kwargs) {
    $(kwargs.dom_ident).append(kwargs.text);
  }
}

function SniperRefreshHandler() {
  this.ident = '__bi_refresh';
  this.handle = function(source, kwargs) {
    location.reload();
  }
}

function SniperRedirect() {
  this.ident = '__bi_redirect';
  this.handle = function(source, kwargs) {
    window.location.replace(kwargs.href)
  }
}

function SniperAlertDialogHandler() {
  this.ident = '__bi_alert';
  this.handle = function(source, kwargs) {
    window.alert(kwargs.text);
  }
}

function SniperSetCSSHandler() {
  this.ident = '__bi_set_css';
  this.handle = function(source, kwargs) {
    var elements = $(kwargs.selector);
    var css = kwargs.values;
    for (var key in css) {
      elements.css(key, css[key]);
    }
  }
}

function SniperJSCallHandler() {
  this.ident = '__bi_js_call';
  this.handle = function(source, kwargs) {
    var name = kwargs.name;
    var args = kwargs.args;
    if (window[name]){
      window[name].apply(null, args);
    }
  }
}

function SniperPushStateHandler() {
  this.ident = '__bi_push_state';
  this.handle = function(source, kwargs) {
    var url = kwargs.url;
    history.pushState({}, "none", url);
  }
}

var $sniper = new Sniper();
