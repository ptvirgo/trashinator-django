module Models exposing (..)

import Date

type Amount = Gallons Float | Litres Float

type alias Trash =
    { date : Date.Date
    , amount : Amount
    }

type alias TrashPage =
    { trash : Maybe Trash 
    , error : Maybe String
    }

emptyTrash : Trash
emptyTrash =
    { date = Date.fromTime 0
    , amount = Gallons 0
    }
