/* global Vue, VueQrcode, _, Quasar, LOCALE, windowMixin, LNbits */

Vue.component(VueQrcode.name, VueQrcode)

var locationPath = [
  window.location.protocol,
  '//',
  window.location.host,
  window.location.pathname
].join('')

var locationHost = [window.location.protocol, '//', window.location.host].join(
  ''
)

var mapsatoshigogame = function (obj) {
  obj._data = _.clone(obj)
  obj.date = Quasar.utils.date.formatDate(
    new Date(obj.time * 1000),
    'YYYY-MM-DD HH:mm'
  )
  obj.tleft = obj.top_left
  obj.bright = obj.bottom_right
  obj.satoshigo_url = [locationPath, obj.hash].join('')

  return obj
}

var mapsatoshigoplayers = function (obj) {
  obj._data = _.clone(obj)
  obj.inkey = obj.inkey
  obj.name = obj.user_name
  obj.game_id = obj.game_id
  return obj
}

new Vue({
  el: '#vue',
  mixins: [windowMixin],
  data: function () {
    return {
      checker: null,
      satoshigogames: [],
      satoshigoplayers: [],
      satoshigogamesTable: {
        columns: [
          {name: 'hash', align: 'left', label: 'ID', field: 'hash'},
          {name: 'title', align: 'left', label: 'Title', field: 'title'},
          {name: 'description', align: 'left', label: 'Title', field: 'description'},
          {name: 'totalFunds', align: 'left', label: 'totalFunds', field: 'totalFunds'},
          {name: 'fundsCollected', align: 'left', label: 'fundsCollected', field: 'fundsCollected'}
        ],
        pagination: {
          rowsPerPage: 10
        }
      },
      satoshigoplayersTable: {
        columns: [
          {name: 'inkey', align: 'left', label: 'ID', field: 'inkey'},
          {name: 'user_name', align: 'left', label: 'Name', field: 'user_name'},
          {name: 'game_id', align: 'left', label: 'Game ID', field: 'game_id'}
        ],
        pagination: {
          rowsPerPage: 10
        }
      },
      formDialog: {
        show: false,
        data: {
          is_unique: false
        }
      },
      qrCodeDialog: {
        show: false,
        data: null
      }
    }
  },
  computed: {
    sortedsatoshigogames: function () {
      return this.satoshigogames.sort(function (a, b) {
        return
      })
    },
    sortedsatoshigoplayers: function () {
      return this.satoshigoplayers.sort(function (a, b) {
        return
      })
    }
  },
  methods: {
    test: function () {
    },
    getsatoshigogames: function () {
      var self = this

      LNbits.api
        .request(
          'GET',
          '/satoshigo/api/v1/admin/games?all_wallets',
          this.g.user.wallets[0].inkey
        )
        .then(function (response) {
          self.satoshigogames = response.data.map(function (obj) {
            return mapsatoshigogame(obj)
          })
        })
        .catch(function (error) {
          clearInterval(self.checker)
          LNbits.utils.notifyApiError(error)
        })
    },
    getsatoshigoplayers: function () {
      var self = this

      LNbits.api
        .request(
          'GET',
          '/satoshigo/api/v1/games/players',
          this.g.user.wallets[0].inkey
        )
        .then(function (response) {
          self.satoshigoplayers = response.data.map(function (obj) {
            return mapsatoshigoplayers(obj)
          })
        })
        .catch(function (error) {
          clearInterval(self.checker)
          LNbits.utils.notifyApiError(error)
        })
    },
    closeFormDialog: function () {
      this.formDialog.data = {
        is_unique: false
      }
    },
    openQrCodeDialog: function (gameId) {
      var game = _.findWhere(this.satoshigogames, {id: gameId})

      this.qrCodeDialog.data = _.clone(game)

      this.qrCodeDialog.data.url =
        window.location.protocol + '//' + window.location.host
      this.qrCodeDialog.show = true
    },
    openUpdateDialog: function (gameId) {
      var game = _.findWhere(this.satoshigogames, {id: gameId})
      this.formDialog.data = _.clone(game._data)
      this.formDialog.show = true
    },
    sendFormData: function () {
      var wallet = _.findWhere(this.g.user.wallets, {
        id: this.formDialog.data.wallet
      })
      var data = _.omit(this.formDialog.data, 'wallet')
      if (data.id) {
        this.updatesatoshigogame(wallet, data)
      } else {
        this.createsatoshigogame(wallet, data)
      }
    },
    simplesendFormData: function () {
      var wallet = _.findWhere(this.g.user.wallets, {
        id: this.simpleformDialog.data.wallet
      })
      var data = _.omit(this.simpleformDialog.data, 'wallet')

      data.title = 'game'

      if (data.id) {
        this.updatesatoshigogame(wallet, data)
      } else {
        this.createsatoshigogame(wallet, data)
      }
    },
    updatesatoshigogame: function (wallet, data) {
      var self = this

      LNbits.api
        .request(
          'PUT',
          '/satoshigo/api/v1/games/' + data.id,
          wallet.adminkey,
          _.pick(data, 'title', 'description', 'top_left', 'bottom_right')
        )
        .then(function (response) {
          self.satoshigogames = _.reject(self.satoshigogames, function (obj) {
            return obj.id === data.id
          })
          self.satoshigogames.push(mapsatoshigogame(response.data))
          self.formDialog.show = false
        })
        .catch(function (error) {
          LNbits.utils.notifyApiError(error)
        })
    },
    createsatoshigogame: function (wallet, data) {
      var self = this

      LNbits.api
        .request('POST', '/satoshigo/api/v1/games', wallet.adminkey, data)
        .then(function (response) {
          self.satoshigogames.push(mapsatoshigogame(response.data))
          self.formDialog.show = false
          self.simpleformDialog.show = false
        })
        .catch(function (error) {
          LNbits.utils.notifyApiError(error)
        })
    },
    deletesatoshigogame: function (gameId) {
      var self = this
      var game = _.findWhere(this.satoshigogames, {hash: gameId})

      LNbits.utils
        .confirmDialog('Are you sure you want to delete this satoshigo game?')
        .onOk(function () {
          LNbits.api
            .request(
              'DELETE',
              '/satoshigo/api/v1/games/' + gameId,
              _.findWhere(self.g.user.wallets, {id: game.wallet}).adminkey
            )
            .then(function (response) {
              self.satoshigogames = _.reject(
                self.satoshigogames,
                function (obj) {
                  return obj.hash === gameId
                }
              )
            })
            .catch(function (error) {
              LNbits.utils.notifyApiError(error)
            })
        })
    },
    exportCSV: function () {
      LNbits.utils.exportCSV(this.paywallsTable.columns, this.paywalls)
    }
  },
  created: function () {
    if (this.g.user.wallets.length) {
      var getsatoshigogames = this.getsatoshigogames
      getsatoshigogames()
      var getsatoshigoplayers = this.getsatoshigoplayers
      getsatoshigoplayers()
    }
  }
})
