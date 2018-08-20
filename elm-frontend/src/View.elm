module View exposing (..)

import Html exposing (..)
import Html.Attributes exposing (..)
import Html.Events exposing (..)

import Trash.Enum.Metric exposing (Metric (..))

import Model exposing (..)
import Update exposing (..)

view : Model -> Html Msg
view model = div []
    [ viewTrash model.volume model.metric model.day
    , inputVolume model.metric
    , saveButton model.error
    , viewErrors model.error
    ]

viewTrash : Maybe Float -> Metric -> WhichDay -> Html Msg
viewTrash amount metric day =
    let metricWord = metric |> toString |> String.toLower
        howMuch = case amount of
            Nothing -> "nothing"
            (Just x) -> (toString x) ++ " " ++ metricWord ++ " of trash "
        when = whichDayToString day 
    in p [] [ text <| "I took out " ++ howMuch ++ " " ++ when  ++ "." ]

inputVolume : Metric -> Html Msg
inputVolume metric = p []
    [ input [ placeholder "How much?", onInput ChangeAmount ] []
    , text <| " " ++ (metric |> toString |> String.toLower) ++ " of trash"
    ]

saveButton : Maybe String -> Html Msg
saveButton error = case error of
    Nothing -> p [ onClick SavePage ] [ text "Save" ]
    (Just _) -> text ""

viewErrors : Maybe String -> Html Msg
viewErrors error = case error of
        Nothing -> text ""
        (Just msg) -> p [ class "error" ] [ text <| "(" ++ msg ++ ")" ]

