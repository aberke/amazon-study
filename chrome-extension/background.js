// A place for persistant variables

// ACTUALLY maybe the things below do not belong here?

const PROJECTURL = "https://aberke.github.io/amazon-study";

// TODO: randomly assign experiment arm
// and/or grab from URL parameter

// string
let dataID = null; // Null until the data is scraped
// datetime
let lastUploaded = null; // null until data uploaded.


// On installation or update:
// Navigate to the project page if not already there.
chrome.runtime.onInstalled.addListener((reason) => {
    console.log("was installed or updated:", reason)
    chrome.tabs.query({
        active: true,
        lastFocusedWindow: true
    }, function(tabs) {
        let activeTab = tabs[0];
        if (activeTab.url.indexOf(PROJECTURL) != 0) {
            chrome.tabs.create({
                url: PROJECTURL
            });
        }
    });
});
