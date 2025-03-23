document.getElementById("uploadForm").addEventListener("submit", function(event) {
    event.preventDefault();

    let formData = new FormData();
    formData.append("job_description", document.getElementById("job_description").value);

    let files = document.getElementById("resumes").files;
    for (let i = 0; i < files.length; i++) {
        formData.append("resumes", files[i]);
    }

    fetch("/upload", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        let resultsTable = document.getElementById("resultsTable");
        resultsTable.innerHTML = `
            <tr>
                <th>Rank</th>
                <th>Candidate</th>
                <th>Skills</th>
                <th>Experience</th>
                <th>Match Score</th>
            </tr>
        `;

        data.forEach((resume, index) => {
            let row = resultsTable.insertRow();
            row.insertCell(0).innerText = index + 1;
            row.insertCell(1).innerText = resume.name;
            row.insertCell(2).innerText = resume.skills.join(", ");
            row.insertCell(3).innerText = resume.experience.join(", ");
            row.insertCell(4).innerText = resume.score + "%";
        });
    });
});
