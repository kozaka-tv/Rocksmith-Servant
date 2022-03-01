// ==UserScript==
// @name         RS Playlist enhancer and simplifier
// @namespace    http://tampermonkey.net/
// @version      0.2
// @description  Removes unnecessary elements from the page like Logo and footer and reads out from the cookies the PHPSESSID value and puts it to the bottom of the list.
// @author       kozaka
// @match        https://rsplaylist.com/*
// @icon         https://rsplaylist.com/favicon-32x32.png
// @grant        none
// @require      file://c:\work\kozaka-tv\Rocksmith-Servant\misc\tampermonkey\RS Playlist enhancer and simplifier.user.js
// @homepage     https://github.com/kozaka-tv/Rocksmith-Servant
// @homepageURL  https://github.com/kozaka-tv/Rocksmith-Servant
// @downloadURL  https://github.com/kozaka-tv/Rocksmith-Servant/blob/main/misc/tampermonkey/RS%20Playlist%20enhancer%20and%20simplifier.user.js
// @updateURL    https://github.com/kozaka-tv/Rocksmith-Servant/blob/main/misc/tampermonkey/RS%20Playlist%20enhancer%20and%20simplifier.user.js
// @supportURL   https://github.com/kozaka-tv/Rocksmith-Servant/issues
// ==/UserScript==
/* globals jQuery, $, waitForKeyElements */

(
    function () {
        'use strict';

        $("div.logo").remove();
        $("div.footer").remove();

        $('div.content').attr('style', 'width: 95%');
        $('div.request-header-columns').attr('style', 'display: flex; align-items: stretch; flex-direction: row; margin-bottom: 00px;');

        $("div.playlist").append(`
            <div class="cookie" style="color: white; text-align: center; padding: 10px">
                <input type="hidden" name="PHPSESSID" value="` + extractPHPSESSIDFromCookie() + `" id="myInput">
                <button id="copyButton">Copy your PHPSESSID to clipboard</button>
            </div>
        `);

        $('#copyButton').click(function (event) {
            copyToClipboard();
        });

        function extractPHPSESSIDFromCookie() {
            if (document.cookie.split(';').some((item) => item.trim().startsWith('PHPSESSID='))) {
                return document.cookie
                    .split('; ')
                    .find(row => row.startsWith('PHPSESSID='))
                    .split('=')[1];
            }
            return "";
        }

        function copyToClipboard() {
            let phpsessidElement = document.getElementsByName("PHPSESSID")[0];
            phpsessidElement.select();
            navigator.clipboard.writeText(phpsessidElement.value);
            alert("Your PHPSESSID has been copied to the clipboard!\n(PHPSESSID = " + phpsessidElement.value + ")");
        }

    }
)();
