module TrashPageMain exposing (main)

import Html exposing (programWithFlags)
import Date exposing (fromTime)
import Time 

import Models exposing (..)
import UpdateTrashPage exposing (updateTrashPage)
import ViewTrashPage exposing (viewTrashPage)

type alias Flags =
    { token : String
    , timeStamp : Time.Time
    , metric : String
    }

importArgs : Flags -> TrashPage
importArgs flags =
    let amount = case flags.metric of
        "litres" -> Litres 0
        _ -> Gallons 0
    in
        { token = flags.token
        , error = Nothing
        , trash = Just
            { date = fromTime flags.timeStamp
            , amount = amount
            }
        }

main = programWithFlags
    { init = \flags -> (importArgs flags, Cmd.none)
    , view = viewTrashPage
    , update = updateTrashPage
    , subscriptions = (\_ -> Sub.none)
    }
