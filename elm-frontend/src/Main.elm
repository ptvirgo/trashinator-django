module Main exposing (..)

import Html exposing (..)
import Time exposing (every, second)
import Date

import Trash.Enum.Metric exposing (Metric (..))

import Model exposing (Model, Jwt (..), emptyPage)
import Update exposing (Msg, update, savePage)
import View exposing (view)

type alias Flags =
    { timestamp : Float
    , token : String
    , metric : String
    }

init : Flags -> ( Model, Cmd Msg )
init flags =
    let readMetric s = case s of
            "Litres" -> Litres
            _ -> Gallons
        newPage =
            { emptyPage
            | jwt = Jwt flags.token
            , timestamp = flags.timestamp
            , metric = readMetric flags.metric
            }
    in
    ( newPage, savePage newPage )
    

main : Program Flags Model Msg
main = Html.programWithFlags
    { init = init
    , update = update
    , subscriptions = \_ -> Sub.none
    , view = view
    }
