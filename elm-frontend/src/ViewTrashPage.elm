module ViewTrashPage exposing (..)

import Html exposing (..)
import Html.Attributes exposing (..)
import Html.Events exposing (..)

import Models exposing (..)
import UpdateTrashPage exposing (..)

viewTrashPage : TrashPage -> Html Msg
viewTrashPage page = Html.form [ id "trashForm" ]
    [ viewTrash page.trash
    , viewError page.error
    ]

viewTrash : Maybe Trash -> Html Msg
viewTrash trashState = case trashState of
    Nothing -> p [ class "status" ] [ text "Please wait." ]
    (Just trash) -> div []
        [ p [ class "status" ]
            [ text <| "I took out " ++ sayAmount trash.amount ++ " today." ]
        , p [ id "inputTrashAmount" ]
            [ input [ placeholder "how much?", onInput ChangeAmount ] []
            , text <| " " ++ (amountWord trash.amount) ++ "s of trash"
            ]
        ]

viewError : Maybe String -> Html Msg
viewError errState = case errState of
    Nothing -> text ""
    (Just error) -> p [class "error" ] [ text error ]

-- Helpers

amountWord : Amount -> String
amountWord amt = case amt of
    (Gallons _) -> "gallon"
    (Litres _) -> "litre"

sayAmount : Amount -> String
sayAmount amt =
    let measure = amountWord amt
        x = case amt of
            (Gallons a) -> a
            (Litres a) -> a
    in
        if x == 0 then "nothing"
        else if x == 1 then (toString x) ++ " " ++ measure ++ " of trash"
        else (toString x) ++ " " ++ measure ++ "s" ++ " of trash"
