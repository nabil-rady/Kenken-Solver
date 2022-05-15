function cellToString(cell) {
    return `x${cell[0]}y${cell[1]}`;
}

function isNeighbour(cell1, cell2) {
    return (cell1[0] === cell2[0] && Math.abs(cell1[1] - cell2[1]) === 1) ||
        (cell1[1] === cell2[1] && Math.abs(cell1[0] - cell2[0]) === 1);
}

function getNeighbourDirection(cell1, cell2) {
    let neighboursString = '';
    if (cell1[0] > cell2[0])
        neighboursString += 'u';
    else if (cell1[0] < cell2[0])
        neighboursString += 'd';
    if (cell1[1] > cell2[1])
        neighboursString += 'l';
    else if (cell1[1] < cell2[1])
        neighboursString += 'r';
    return neighboursString;
}

function getNeighboursSides(cellGroup, index) {
    const cellInQuestion = cellGroup[index];
    let sidesToBeRemoved = '';
    for (const cell of cellGroup) {
        if (cellToString(cell) === cellToString(cellInQuestion))
            continue;
        if (isNeighbour(cell, cellInQuestion)) {;
            sidesToBeRemoved += getNeighbourDirection(cellInQuestion, cell);
        }
    }
    return sidesToBeRemoved;
}

function removeSides(cellGroup, index, sidesToBeRemoved) {
    const cell = cellGroup[index];
    for (const char of sidesToBeRemoved) {
        if (char === 'l')
            document.querySelector(`#${cellToString(cell)}`).classList.remove('left');
        else if (char === 'r')
            document.querySelector(`#${cellToString(cell)}`).classList.remove('right');
        else if (char === 'u')
            document.querySelector(`#${cellToString(cell)}`).classList.remove('top');
        else if (char === 'd')
            document.querySelector(`#${cellToString(cell)}`).classList.remove('bottom');
    }
}

function scanForNeighbours(cellGroup) {
    for (const [index, _] of Object.entries(cellGroup)) {
        const sidesToBeRemoved = getNeighboursSides(cellGroup, index);
        removeSides(cellGroup, index, sidesToBeRemoved);
    }
}

function putCageSymbol(cellGroupInfo) {
    const [cellGroup, symbol, number] = cellGroupInfo;
    let cageSymbolElement = document.createElement('div');
    cageSymbolElement.style = `position: absolute; top: 3px; left: 3px; font-size: 1rem; font-weight: bold;`
    if (symbol !== '.') {
        cageSymbolElement.textContent = `${symbol}(${number})`;
    } else {
        cageSymbolElement.textContent = `${number}`;
    }
    document.querySelector(`#${cellToString(cellGroup[0])}`).appendChild(cageSymbolElement); // = `content: ${symbol}${number}; `;
}

async function printBoard(i_BoardSize) {
    const generatedBoard = await getBoard(i_BoardSize);
    let board = document.getElementById('board');
    board.innerHTML = '';
    let table = document.createElement('table');
    let tbody = document.createElement('tbody');
    for (let x = 0; x < i_BoardSize; ++x) {
        let tr = document.createElement('tr');
        for (let y = 0; y < i_BoardSize; ++y) {
            let td = document.createElement('td');
            td.id = cellToString([x + 1, y + 1]);
            td.classList.add('top');
            td.classList.add('bottom');
            td.classList.add('left');
            td.classList.add('right');
            tr.appendChild(td);
        }
        tbody.appendChild(tr);
    }
    table.appendChild(tbody);

    board.appendChild(table);

    for (const cellGroupInfo of generatedBoard) {
        const cellGroup = cellGroupInfo[0];
        scanForNeighbours(cellGroup);
        putCageSymbol(cellGroupInfo);
    }
}

const getBoard = async (size) => {
    let board = await fetch('http://localhost:5000/generate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            size: size
        })
    });

    board = await board.json();
    return board.board;
}

document.querySelector('#generate').addEventListener('click', () => printBoard(document.getElementById('size').value));

const getSolution = async (algo) => {
    if(algo !== 'bt' && algo !== 'fc' && algo !== 'ac3')
        throw new Error('Incorrect algorithm string.')
    let board = await fetch(`http://localhost:5000/${algo}`, {
        method: 'GET',
    });

    board = await board.json();
    return board.solution;
}

async function solve(i_BoardSize) {
    const inputData = document.getElementsByName('algorithm');
    let algorithm = '';
    for(i = 0; i < inputData.length; i++) {
        if(inputData[i].checked){
            algorithm = inputData[i];
            break;
        }
    }
    console.log(algorithm.value)
    const solution = await getSolution(algorithm.value);
    for (let x = 0; x < i_BoardSize; ++x) {
        for (let y = 0; y < i_BoardSize; ++y) {
            let tableData = document.querySelector(`#x${x+1}y${y+1}`);
            let index = tableData.innerHTML.search('<div')
            if(index===-1)
            {
                tableData.innerHTML=''
            }
            else {
                tableData.innerHTML=''+tableData.innerHTML.substring(index,tableData.length)
            }
            for(let i=0;i<solution.length;i++)
            {
                for(let j=0; j<solution[i][0].length;j++)
                {
                    console.log()
                    if(solution[i][0][j][0]=== x+1 && solution[i][0][j][1]===y+1)
                    {
                        tableData.innerHTML = solution[i][1][j]+tableData.innerHTML
                    }

                }
            }
        }
    }
}

document.querySelector('#solve').addEventListener('click', () => solve(document.getElementById('size').value));
