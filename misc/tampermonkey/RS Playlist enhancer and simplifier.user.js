// ==UserScript==
// @name         RS Playlist enhancer and simplifier
// @namespace    http://tampermonkey.net/
// @version      0.1
// @description  Removes unnecessary elements from the page like Logo and footer and reads out from the cookies the PHPSESSID value and puts it to the bottom of the list.
// @author       kozaka
// @match        https://rsplaylist.com/playlist/*
// @icon         https://rsplaylist.com/favicon-32x32.png
// @grant        none
// @require      @require http://code.jquery.com/jquery-3.6.0.min.js
// ==/UserScript==


(function () {
    'use strict';

    $("div.logo").remove();
    $("div.footer").remove();

    $('div.content').attr('style', 'width: 95%');
    $('div.request-header-columns').attr('style', 'display: flex; align-items: stretch; flex-direction: row; margin-bottom: 00px;');

    $("div.playlist").append(`<div class="cookie" style="color: white; text-align: center"><p>` + document.cookie + `</p></div>`);

})();
