module TrashPage.View exposing (..)

import Html exposing (..)
import Html.Attributes exposing (..)
import Html.Events exposing (..)

import Trash.Enum.Metric exposing (Metric (..))

import TrashPage.Model exposing (..)
import TrashPage.Update exposing (..)

saveButtonIcon : String
saveButtonIcon = "/static/trashinator/checkmark.svg"

noSaveButtonIcon : String
noSaveButtonIcon = "/static/trashinator/checkmark-faded.svg"


view : Model -> Html Msg
view model = div []
    [ viewTrash model.volume model.metric model.day
    , inputVolume model.metric
    , saveButton model
    , viewStats model
    , viewErrors model.error
    ]

viewTrash : Maybe Float -> Metric -> WhichDay -> Html Msg
viewTrash amount metric day =
    let metricWord = metric |> toString |> String.toLower
        howMuch = case amount of
            Nothing -> "..."
            (Just 0) -> "nothing"
            (Just x) -> (toString x) ++ " " ++ metricWord ++ " of trash "
        when = whichDayToString day 
    in p [ id "trashSentence" ] [ text <| "I took out " ++ howMuch ++ " " ++ when  ++ "." ]

inputVolume : Metric -> Html Msg
inputVolume metric = p [ id "trashAmount" ]
    [ input [ placeholder "How many?", onInput ChangeAmount ] []
    , text <| " " ++ (metric |> toString |> String.toLower) ++ " of trash"
    ]

saveButton : Model -> Html Msg
saveButton model = 
    if model.changed && model.error == Nothing && model.volume /= Nothing
    then
        img [ onClick SavePage
            , id "saveButton"
            , src saveButtonIcon
            , alt "save"
            ] []
    else
        img [ id "saveButton" , src noSaveButtonIcon, alt "can't save" ] []

viewStats : Model -> Html Msg
viewStats model = p [ class "stats" ]
    [ text <| "The average is "
    ++  toString model.stats.perPersonPerWeek
    ]

viewErrors : Maybe String -> Html Msg
viewErrors error = case error of
        Nothing -> text ""
        (Just msg) -> p [ class "error" ] [ text <| "(" ++ msg ++ ")" ]
