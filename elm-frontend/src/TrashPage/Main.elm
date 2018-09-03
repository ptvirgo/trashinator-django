module TrashPage.Main exposing (..)

import Html exposing (..)
import Time exposing (every, second)
import Date

import Trash.Enum.Metric exposing (Metric (..))

import TrashPage.Model exposing (..)
import TrashPage.Update exposing (Msg, update, lookupTrash, lookupStats)
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
        emptyMeta = emptyPage.meta
        emptyEntry = emptyPage.entry
        newPage =
            { emptyPage
            | meta = { emptyMeta | timestamp = flags.timestamp }
            , entry =
                { emptyEntry
                | jwt = Jwt flags.token
                , metric = readMetric flags.metric
                , date = relativeDate flags.timestamp Today
                }
            }
    in
    ( newPage, Cmd.batch [ lookupTrash newPage, lookupStats newPage ] )

main : Program Flags Model Msg
main = Html.programWithFlags
    { init = init
    , update = update
    , subscriptions = \_ -> Sub.none
    , view = view
    }
