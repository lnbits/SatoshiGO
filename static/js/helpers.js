/** @format */

export function chunkArray(myArray, chunk_size) {
  var index = 0
  var arrayLength = myArray.length
  var tempArray = []

  for (index = 0; index < arrayLength; index += chunk_size) {
    var myChunk = myArray.slice(index, index + chunk_size)
    tempArray.push(myChunk)
  }

  return tempArray
}

export function getIndexOfK(arr, k) {
  for (var i = 0; i < arr.length; i++) {
    var index = arr[i].indexOf(k)
    if (index > -1) {
      return [i, index]
    }
  }
}
