const glob = require('glob')
const fs = require('fs-extra')
const path = require('path')

const [srcRoot, dstRoot] = process.argv.slice(2)

glob(`${srcRoot}/**/*.*`, { ignore: '*~' }, (err, files) => {
  if (err) {
    console.log(err)
  } else {
    for (const srcName of files) {
      const dstName = srcName.replace(srcRoot, dstRoot)
      const dstDir = path.dirname(dstName)
      fs.ensureDir(dstDir, (err) => {
        if (err) {
          console.error(err)
        }
      })
    }
  }
})