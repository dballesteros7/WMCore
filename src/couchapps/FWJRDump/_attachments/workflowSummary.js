function getRootDBPath() {
  // Figure out the root DB path given the current url of the page.  This will
  // return just the hostname and the database name with /jobs or /fwjrs.
  var urlParts = location.href.split('/');
  var rootDBName = urlParts[3].split('%2F')[0];
  return "http://" + urlParts[2] + "/" + rootDBName;
}

function getFailedJobs(workflowName, statusDiv) {
  // Retrieve the list of failed jobs IDs from couch for the given workflow.
  statusDiv.innerHTML = "Retrieving list of failed jobs from couch...";
  xmlhttp = new XMLHttpRequest();
  xmlhttp.open("GET", getRootDBPath() + "%2Fjobs/_design/JobDump/_view/failedJobsByWorkflowName?stale=ok&include_docs=true&startkey=[\"" + workflowName + "\"]&endkey=[\"" + workflowName + "\",{}]", false);
  xmlhttp.send();

  statusDiv.innerHTML += "done.";
  return eval("(" + xmlhttp.responseText + ")")["rows"];
};

function getErrorInfo(workflowName, statusDiv) {
  // Retrieve the error information from couch for the given workflow.
  statusDiv.innerHTML = "Retrieving errors messages from couch...";
  xmlhttp = new XMLHttpRequest();
  xmlhttp.open("GET", getRootDBPath() + "%2Ffwjrs/_design/FWJRDump/_view/errorsByWorkflowName?stale=ok&startkey=[\"" + workflowName + "\"]&endkey=[\"" + workflowName + "\",{}]", false);
  xmlhttp.send();
  statusDiv.innerHTML += "done.";
  return eval("(" + xmlhttp.responseText + ")")["rows"];
};

function numericalCompare(a, b) {
  return a - b;
}

function removeArrayDuplicates(someArray, compareFunc) {
  // Given two arrays remove all duplicate entries and return a new array. If
  // the compareFunc argument is "numberical" the returned array will be sorted
  // in numerical order, otherwise it will be sorted in dictionary order.
  var uniqueValues = new Array;
  var prevValue = null;

  if (compareFunc == "numerical") {
    someArray.sort(numericalCompare);
  } else {
    someArray.sort();
  }

  for (var arrayIndex in someArray) {
    if (prevValue != someArray[arrayIndex]) {
      uniqueValues.push(someArray[arrayIndex]);
      prevValue = someArray[arrayIndex];
    };
  };

  return uniqueValues;
}

function collateFailureInfo(failedJobs, fwjrInfo, statusDiv) {
  // Given a list of failed job IDs retrieve the frameworks job reports for all
  // of the jobs and sort the failure information into a single object.  The 
  // object will have the following form:
  //  {taskName: {stepName: {exitCode: {"errors": [{"type": type, "exitCode": exitCode,
  //                                     "details": details}, ...],
  //                                    "jobs": [jobID, ...],
  //                                    "input": [lfn, ...],
  //                                    "runs": {runNumber: [lumi, ...]}}}}
  var workflowFailures = {};
  var missedRunLumi = {};
  var errorInfo = {};

  for (var fwjrIndex in fwjrInfo) {
    jobID = fwjrInfo[fwjrIndex]["value"]["jobid"];
    if (errorInfo.hasOwnProperty(jobID)) {
      errorInfo[jobID] = errorInfo[jobID].concat(fwjrInfo[fwjrIndex]["value"]);
    } else {
      errorInfo[jobID] = [fwjrInfo[fwjrIndex]["value"]];
    };
  };

  failedJobs.sort(numericalCompare);
  for (var failedJobIndex in failedJobs) {
    var jobID = failedJobs[failedJobIndex]["value"];
    var jobDoc = failedJobs[failedJobIndex]["doc"];
    var jobErrors = errorInfo[jobID];

    statusDiv.innerHTML = "Processing failure information for job " + jobID + " ";
    statusDiv.innerHTML += "(" + failedJobIndex + " of " + failedJobs.length + ")";

    for (var errorIndex in jobErrors) {
      var workflowError = jobErrors[errorIndex];
      if (!workflowFailures.hasOwnProperty(workflowError["task"])) {
        workflowFailures[workflowError["task"]] = {};
      }

      var taskFailure = workflowFailures[workflowError["task"]]
      if (!taskFailure.hasOwnProperty(workflowError["step"])) {
        taskFailure[workflowError["step"]] = {};
      };

      var stepFailure = taskFailure[workflowError["step"]];
      exitCode = workflowError["error"][0]["exitCode"] + "";
      if (!stepFailure.hasOwnProperty(exitCode)) {
        stepFailure[exitCode] = {"errors": new Array(),
                                 "jobs": new Array(),
                                 "input": new Array(),
                                 "runs": {}};

        for (fwjrErrorIndex in workflowError["error"]) {
          stepFailure[exitCode]["errors"].push(workflowError["error"][fwjrErrorIndex]);
        };
      };

      for(var inputIndex in jobDoc["inputfiles"]) {
        stepFailure[exitCode]["input"] = stepFailure[exitCode]["input"].concat(jobDoc["inputfiles"][inputIndex]["lfn"]);
      };

      stepFailure[exitCode]["jobs"].push(jobID);

      if (jobDoc["mask"].runAndLumis) {
        for(var runNumber in jobDoc["mask"]["runAndLumis"]) {
          for(var lumiIndex in jobDoc["mask"]["runAndLumis"][runNumber]) {
            firstLumi = jobDoc["mask"]["runAndLumis"][runNumber][lumiIndex][0];
            lastLumi = jobDoc["mask"]["runAndLumis"][runNumber][lumiIndex][1];
            var lumis = [];
            while (firstLumi <= lastLumi) {
              lumis.push(firstLumi);
              firstLumi += 1;
            }
            if (stepFailure[exitCode]["runs"].hasOwnProperty(runNumber)) {
              stepFailure[exitCode]["runs"][runNumber] = stepFailure[exitCode]["runs"][runNumber].concat(lumis);
            } else {
              stepFailure[exitCode]["runs"][runNumber] = lumis;
            };

            if (missedRunLumi.hasOwnProperty(runNumber)) {
              missedRunLumi[runNumber] = missedRunLumi[runNumber].concat(lumis);
            } else {
              missedRunLumi[runNumber] = lumis;
            };
          };
        };
      };
    };
  };

  renderRunLumiDetails(missedRunLumi, document.getElementById("runlumi"), false);
  return workflowFailures;
}

function renderErrorDetails(errorInfo, stepDiv) {
  // Insert the error information into the given div.
  for(var errorIndex in errorInfo) {
    stepError = errorInfo[errorIndex];
    var errorDiv = document.createElement("div");

    if (errorIndex == 0) {
      errorDiv.style.margin = "5px 0px 0px 15px";
    } else {
      errorDiv.style.margin = "10px 0px 0px 15px";
    }

    errorDiv.innerHTML = "<b>Error Type:</b> " + stepError["type"] + "<br>";
    errorDiv.innerHTML += "<b>Error Code:</b> " + stepError["exitCode"] + "<br>";
    errorDiv.innerHTML += "<b>Error Details:</b>";
    stepDiv.appendChild(errorDiv);

    var errorDetailsPre = document.createElement("pre");
    errorDetailsPre.style.margin = "0px 0px 0px 15px";
    errorDetailsPre.style.backgroundColor = "silver";
    errorDetailsPre.style.marginTop = "0px";
    errorDetailsPre.style.marginBottom = "0px";
    errorDetailsPre.style.width = "100%";
    errorDetailsPre.innerHTML = stepError["details"];
    errorDiv.appendChild(errorDetailsPre);
  };
};

function renderJobDetails(jobIDs, stepDiv) {
  // Insert job information into the given div.
  var uniqueJobIDs = removeArrayDuplicates(jobIDs, "numerical");

  var failedJobCountDiv = document.createElement("div");
  failedJobCountDiv.style.margin = "10px 0px 0px 15px";
  stepDiv.appendChild(failedJobCountDiv);

  if (uniqueJobIDs.length == 1) {
    var failedJobsLabel = "<b>" + "1 job failed ";
  } else {
    var failedJobsLabel = "<b>" + uniqueJobIDs.length + " jobs failed ";
  }

  if (jobIDs.length == 1) {
    failedJobsLabel += "1 time:</b>";
  } else {
    failedJobsLabel += jobIDs.length + " times:</b>";
  }
  failedJobCountDiv.innerHTML = failedJobsLabel;  

  var failedJobDiv = document.createElement("div");
  failedJobDiv.style.margin = "0px 0px 0px 15px";
  failedJobCountDiv.appendChild(failedJobDiv);
  var jobCount = 0;
  var failedJobHTML = ""

  for (uniqueJobIndex in uniqueJobIDs) {
    failedJobHTML += "<a href=" + getRootDBPath() + "%2Fjobs/_design/JobDump/_show/jobSummary/" + uniqueJobIDs[uniqueJobIndex] + ">" + uniqueJobIDs[uniqueJobIndex] + "</a> ";
  };

  failedJobDiv.innerHTML = failedJobHTML;
  return;
};

function renderInputDetails(inputLFNs, stepDiv) {
  // Insert input information into the given div.
  if (inputLFNs.length == 0) {
    return;
  }

  var uniqueLFNs = removeArrayDuplicates(inputLFNs, "alphabetical");

  var failedInputCountDiv = document.createElement("div");
  failedInputCountDiv.style.margin = "10px 0px 0px 15px";
  stepDiv.appendChild(failedInputCountDiv);

  if (uniqueLFNs.length == 1) {
    failedInputCountDiv.innerHTML = "<b>1 file was used as input for jobs with this error:</b>";
  } else {
    failedInputCountDiv.innerHTML = "<b>" + uniqueLFNs.length + " files were used as input for jobs with this error:</b>";
  }

  var failedInputDiv = document.createElement("div");
  failedInputDiv.style.margin = "0px 0px 0px 15px";
  failedInputCountDiv.appendChild(failedInputDiv);
  var failedInputList = "";

  for (uniqueInputIndex in uniqueLFNs) {
    failedInputList += uniqueLFNs[uniqueInputIndex] + "<br>";
  };  

  failedInputDiv.innerHTML = failedInputList;
  return;
};

function renderRunLumiDetails(runLumiInfo, stepDiv, heading) {
  // Insert run and lumi information into the given div.
  var runLumiLabelDiv = document.createElement("div");
  runLumiLabelDiv.style.margin = "10px 0px 0px 15px";
  runLumiLabelDiv.innerHTML = "<b>Run Information (all ranges inclusive):</b>";

  var runLumiDiv = document.createElement("div");
  runLumiStr = "";
  runLumiDiv.style.margin = "0px 0px 0px 15px";
  var displayRun = false;

  for (runNumber in runLumiInfo) {
    displayRun = true;
    runLumiStr += runNumber + ": ";
    var rangeBottom;
    var rangeTop;
    uniqueLumis = removeArrayDuplicates(runLumiInfo[runNumber], "numerical");
    for (lumiIndex in uniqueLumis) {
      currentLumi = uniqueLumis[lumiIndex];
      if (lumiIndex == 0) {
        rangeBottom = currentLumi;
        rangeTop = currentLumi;
      } else if (rangeTop + 1 == currentLumi) {
        rangeTop = currentLumi;
      } else {
        if (rangeTop == rangeBottom) {
          runLumiStr += rangeBottom + " ";
        } else {
          runLumiStr += rangeBottom + "-" + rangeTop + " ";
        };

      rangeTop = currentLumi;
      rangeBottom = currentLumi;
      };
    };

    if (rangeTop == rangeBottom) {
      runLumiStr += rangeBottom + " ";
    } else {
      runLumiStr += rangeBottom + "-" + rangeTop + " ";
    };

    runLumiStr += "<br>";
  };  

  if (displayRun) {
    if (heading) {
      stepDiv.appendChild(runLumiLabelDiv);
      runLumiLabelDiv.appendChild(runLumiDiv);
      runLumiDiv.innerHTML = runLumiStr;
    } else {
      stepDiv.appendChild(runLumiDiv);
      runLumiDiv.innerHTML = runLumiStr;
    }
  };
};

function renderWorkflowErrors(workflowName, errorDiv) {
  // Insert workflow error information into the given div.
  errorDiv.style.width = "100%";
  errorDiv.style.height = "100%";

  statusDiv = document.createElement("div");
  statusDiv.style.textAlign = "center";
  statusDiv.style.marginTop = "50px";
  errorDiv.appendChild(statusDiv);

  failedJobs = getFailedJobs(workflowName, statusDiv);
  fwjrInfo = getErrorInfo(workflowName, statusDiv)
  workflowFailures = collateFailureInfo(failedJobs, fwjrInfo, statusDiv);
  var firstTask = true;

  for (var taskName in workflowFailures) {
    var taskDiv = document.createElement("div");
    if (firstTask) {
      firstTask = false;
      taskDiv.style.margin = "0px 0px 0px 15px";
    } else {
      taskDiv.style.margin = "15px 0px 0px 15px";
    };

    taskDiv.innerHTML = "<b>" + taskName + ":</b>";
    errorDiv.appendChild(taskDiv);
    var firstStep = true;

    for(var stepName in workflowFailures[taskName]) {
      var stepDiv = document.createElement("div");

      if (firstStep) {
        firstStep = false;
        stepDiv.style.margin = "0px 0px 0px 15px";
      } else {
        stepDiv.style.margin = "15px 0px 0px 15px";
      };
      stepDiv.innerHTML = "<b>" + stepName + ":</b>";
      taskDiv.appendChild(stepDiv);

      for (var exitCode in workflowFailures[taskName][stepName]) {
        renderErrorDetails(workflowFailures[taskName][stepName][exitCode]["errors"], stepDiv);
        renderJobDetails(workflowFailures[taskName][stepName][exitCode]["jobs"], stepDiv);
        renderInputDetails(workflowFailures[taskName][stepName][exitCode]["input"], stepDiv);
        renderRunLumiDetails(workflowFailures[taskName][stepName][exitCode]["runs"], stepDiv, true);
      };
    };
  };

  errorDiv.removeChild(statusDiv);
  return;
};
