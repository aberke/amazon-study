//popup.js
'use strict';


// good reference:
// https://usefulangle.com/post/339/chrome-extension-create-page-scraper

// start when #start
var startBtn = document.getElementById('start-scraping-btn');
startBtn.classList.add('ready');
startBtn.onclick = function(element) {
    console.log('onclick 1', element)
    startBtn.classList.remove('ready');
    startBtn.classList.add('scraping');
    startBtn.innerHTML = 'scraping...';

    // create a new tab
    // 2021 order history -- TODO: handle pagination after 10 orders
    var url = 'https://www.amazon.com/gp/your-account/order-history?orderFilter=year-2021';
    
	chrome.tabs.query({active: true, currentWindow: true}, async function(tabs) {
        //await goToPage(url, tabs[0].id);
        goToPage(url, tabs[0].id).then( (result) => {
            console.log('goToPage then result', result)
            startBtn.classList.remove('scraping');
            startBtn.innerHTML = 'complete';
            document.body.style.backgroundColor = "white";
        });
	});
};

async function goToPage(url, tab_id) {
	return new Promise(function(resolve, reject) {
		// update current tab with new url
		chrome.tabs.update({url: url});
        document.body.style.backgroundColor = "red";
		
		// fired when tab is updated
		chrome.tabs.onUpdated.addListener(function openPage(tabID, changeInfo) {
			// tab has finished loading, validate whether it is the same tab
			if(tab_id == tabID && changeInfo.status === 'complete') {
				// remove tab onUpdate event as it may get duplicated
				chrome.tabs.onUpdated.removeListener(openPage);


				// fired when content script sends a message
				chrome.runtime.onMessage.addListener(function getDOMInfo(message) {
					// remove onMessage event as it may get duplicated
					chrome.runtime.onMessage.removeListener(getDOMInfo);
                    console.log('getDOMInfo message:', message);

                    // TODO: get the list of orders from the message
                    // go to the prudct url for each order (if available) to scrape the categories from the product page

                    // while the list of orders is > 0: go to next page 

					// save data from message to a JSON file and download
					let json_data = {
						todo: JSON.parse(message).todo,
					};

					let blob = new Blob([JSON.stringify(json_data)], {type: "application/json;charset=utf-8"});
					let objectURL = URL.createObjectURL(blob);
					chrome.downloads.download({ url: objectURL, filename: ('content/amazon-study-purchases/data.json'), conflictAction: 'overwrite' });
				});

				// execute content script
				chrome.scripting.executeScript({                    
                    target: {tabId: tabID},
                    files: ['script.js'],
                }, () => {
					// resolve Promise after content script has executed
					resolve('success');
				});
			}
		});
	});
}
