module TrashPage.Main exposing (..)

import Html exposing (..)
import Time exposing (every, second)
import Date

import Trash.Enum.Metric exposing (Metric (..))

import TrashPage.Model exposing (Model, Jwt (..), emptyPage)
import TrashPage.Update exposing (Msg, update, lookupPage)
import TrashPage.View exposing (view)

type alias Flags =
    { timestamp : Float
    , token : String
    , metric : String
    }

init : Flags -> ( Model, Cmd Msg )
init flags =
    let readMetric s = case String.toLower s of
            "litres" -> Litres
            _ -> Gallons
        newPage =
            { emptyPage
            | jwt = Jwt flags.token
            , timestamp = flags.timestamp
            , metric = readMetric flags.metric
            }
    in
    ( newPage, lookupPage newPage )
    

main : Program Flags Model Msg
main = Html.programWithFlags
    { init = init
    , update = update
    , subscriptions = \_ -> Sub.none
    , view = view
    }
